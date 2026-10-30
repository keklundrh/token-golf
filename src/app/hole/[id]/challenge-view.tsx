"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { Challenge, Option, Skills } from "@/lib/config";
import TokenLedger from "./token-ledger";
import GolfAnimation from "./golf-animation";
import { shouldShowWaitingAnimation } from "@/lib/golf-animation";
import { buildRunBlocks, type RunRecord, type RunRecordUsage } from "@/lib/ledger";
import { formatMicroUsd, formatModelRates, type ModelRates } from "@/lib/currency";

export interface OptionRateInfo {
  modelId: string;
  rates: ModelRates;
}

export interface ChallengeViewProps {
  challenge: Challenge;
  holeCount: number;
  skills: Skills;
  optionRates: Record<string, OptionRateInfo>;
}

interface RunSegment {
  kind: "input" | "output" | "reasoning" | "tools";
  text: string;
}

interface RunState {
  runs: RunRecord[];
  activeIndex: number;
  segments: RunSegment[];
  streaming: boolean;
  error: string | null;
}

export default function ChallengeView({ challenge, holeCount, skills, optionRates }: ChallengeViewProps) {
  const [selected, setSelected] = useState<Option | null>(null);
  const [run, setRun] = useState<RunState>({
    runs: [],
    activeIndex: -1,
    segments: [],
    streaming: false,
    error: null,
  });
  const [recording, setRecording] = useState(false);
  // running total of recorded scores: fetched client-side from the
  // leaderboard API per hole mount; null = still loading (renders "…")
  const [recordedTotalUsd, setRecordedTotalUsd] = useState<number | null>(null);
  const [recordedTotalLoading, setRecordedTotalLoading] = useState(true);
  const outputRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // refresh-safe record: if the user already swung options on this hole
  // (server-side attempts exist), seed recordable runs per option so
  // Record Score works post-reload for any already-run option
  useEffect(() => {
    fetch(`/api/practice?challengeId=${challenge.id}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data: { attempts: Array<{ optionId: string; costUsd: number }> } | null) => {
        if (!data?.attempts?.length) return;
        const records: RunRecord[] = data.attempts.map((a) => {
          const option = challenge.options.find((o) => o.id === a.optionId);
          return {
            optionId: a.optionId,
            optionLabel: option?.label ?? a.optionId,
            timestamp: Date.now(),
            usage: {
              inputTokens: 0,
              outputTokens: 0,
              reasoningTokens: null,
              toolTokens: 0,
              toolCalls: 0,
              inputUsd: 0,
              outputUsd: 0,
              reasoningUsd: 0,
            },
            costUsd: a.costUsd,
            recorded: false,
          };
        });
        setRun((r) => ({ ...r, runs: records, activeIndex: records.length - 1 }));
        const last = data.attempts[data.attempts.length - 1];
        const lastOption = challenge.options.find((o) => o.id === last.optionId);
        if (lastOption) setSelected(lastOption);
      })
      .catch(() => {});
  }, [challenge.id]);

  // Spend header: the player's total of recorded scores, fetched once per
  // hole mount; static while on that hole — recording updates the header on
  // the next hole (loading renders "Spend …", never a false 0)
  useEffect(() => {
    let cancelled = false;
    fetch("/api/leaderboard")
      .then((res) => (res.ok ? res.json() : null))
      .then((data: { leaderboard: Array<{ userId: string; totalUsd: number }>; currentUserId: string | null } | null) => {
        if (cancelled) return;
        const mine = data?.leaderboard.find((e) => e.userId === data.currentUserId);
        setRecordedTotalUsd(mine ? mine.totalUsd : 0);
        setRecordedTotalLoading(false);
      })
      .catch(() => {
        if (!cancelled) setRecordedTotalLoading(false);
      });
    return () => { cancelled = true; };
  }, [challenge.id]);

  useEffect(() => {
    if (run.streaming && outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [run.segments, run.streaming]);

  function practiceSwing() {
    if (!selected || run.streaming || run.runs.some((r) => r.optionId === selected.id)) return;
    setRun((r) => ({ ...r, segments: [], streaming: true, error: null }));

    fetch("/api/practice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ challengeId: challenge.id, optionId: selected.id }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.error ?? `practice swing failed: ${res.status}`);
        }
        if (!res.body) throw new Error("no stream");
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const frames = buffer.split("\n\n");
          buffer = frames.pop() ?? "";
          for (const frame of frames) {
            if (!frame.startsWith("data: ")) continue;
            const event = JSON.parse(frame.slice(6)) as {
              type: string;
              text?: string;
              kind?: string;
              usage?: {
                inputTokens: number;
                outputTokens: number;
                reasoningTokens: number | null;
                toolTokens: number;
                toolCalls: number;
                inputUsd: number;
                outputUsd: number;
                reasoningUsd: number;
                costUsd: number;
              };
            };
            if (event.type === "chunk" && event.text) {
              const kind = (event.kind ?? "output") as RunSegment["kind"];
              const text = event.text;
              setRun((r) => {
                const segments = [...r.segments];
                const last = segments[segments.length - 1];
                if (last && last.kind === kind) {
                  segments[segments.length - 1] = { kind, text: last.text + text };
                } else {
                  segments.push({ kind, text });
                }
                return { ...r, segments };
              });
            } else if (event.type === "done" && event.usage) {
              setRun((r) => {
                const usage: RunRecordUsage = {
                  inputTokens: event.usage!.inputTokens,
                  outputTokens: event.usage!.outputTokens,
                  reasoningTokens: event.usage!.reasoningTokens,
                  toolTokens: event.usage!.toolTokens,
                  toolCalls: event.usage!.toolCalls,
                  inputUsd: event.usage!.inputUsd,
                  outputUsd: event.usage!.outputUsd,
                  reasoningUsd: event.usage!.reasoningUsd,
                };
                const record: RunRecord = {
                  optionId: selected!.id,
                  optionLabel: selected!.label,
                  timestamp: Date.now(),
                  usage,
                  costUsd: event.usage!.costUsd,
                  recorded: false,
                };
                return {
                  ...r,
                  runs: [...r.runs, record],
                  activeIndex: r.runs.length,
                };
              });
            }
          }
        }
        setRun((r) => ({ ...r, streaming: false }));
      })
      .catch((e: Error) =>
        setRun({ runs: [], activeIndex: -1, segments: [], streaming: false, error: e.message }),
      );
  }

  function recordScore() {
    if (!selected || recording || !run.runs.some((r) => r.optionId === selected.id)) return;
    setRecording(true);
    // no cost in the body — the server records its own attempt measurement (#7);
    // the optionId selects which run to keep (#2 steps 14–15)
    fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ challengeId: challenge.id, optionId: selected.id }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`record failed: ${res.status}`);
        setRun((r) => {
          const runs = [...r.runs];
          const idx = runs.findIndex((run) => run.optionId === selected!.id);
          if (idx >= 0) runs[idx] = { ...runs[idx], recorded: true };
          return { ...r, runs };
        });
        router.push(nextHoleUrl());
      })
      .catch((e: Error) => {
        setRecording(false);
        setRun((r) => ({ ...r, error: e.message }));
      });
  }

  function nextHoleUrl(): string {
    const next = challenge.id + 1;
    if (next > holeCount) return "/leaderboard";
    return `/hole/${next}`;
  }

  return (
    <main className="flex min-h-screen flex-col bg-white px-6 py-8 text-black">
      <div className="mx-auto flex w-full max-w-2xl flex-col gap-6">
        <div className="flex items-center justify-between">
          <p className="text-sm text-zinc-500">
            Hole {challenge.id} / {holeCount}
          </p>
          <p className="text-sm text-zinc-500">
            {recordedTotalLoading
              ? "Spend …"
              : `Spend ${formatMicroUsd(recordedTotalUsd ?? 0)}`}
          </p>
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">{challenge.question}</h1>
        <div className="flex flex-col gap-3">
          {challenge.options.map((option) => (
            <button
              key={option.id}
              type="button"
              onClick={() => setSelected(selected?.id === option.id ? null : option)}
              className={`rounded-xl border px-4 py-3 text-left transition-colors ${
                selected?.id === option.id
                  ? "border-green-700 bg-green-50"
                  : "border-zinc-200 hover:border-zinc-400"
              }`}
            >
              <span className="block font-medium">{option.label}</span>
              <span className="block text-sm text-zinc-500">{option.detail}</span>
              {(option.thinking ||
                (option.skills && option.skills.length > 0) ||
                (option.tags && option.tags.length > 0)) && (
                <span className="mt-1.5 flex flex-wrap gap-1.5">
                  {option.thinking && (
                    <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700">
                      thinking{option.thinking !== true ? ` · ${option.thinking}` : ""}
                    </span>
                  )}
                  {option.skills?.map((id) => (
                    <span
                      key={id}
                      className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700"
                    >
                      {skills[id]?.label ?? id}
                    </span>
                  ))}
                  {option.tags?.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-[#EE0000]/10 px-2 py-0.5 text-xs font-medium text-[#CC0000]"
                    >
                      {tag}
                    </span>
                  ))}
                </span>
              )}
              {optionRates[option.id] && (
                <span className="mt-1.5 block border-t border-zinc-100 pt-1.5 font-mono text-xs text-zinc-600">
                  {optionRates[option.id].modelId}
                  <span className="block text-zinc-500">
                    {formatModelRates(optionRates[option.id].rates)}
                  </span>
                </span>
              )}
            </button>
          ))}
        </div>
        {run.segments.length > 0 && (
          <div
            ref={outputRef}
            className="max-h-64 overflow-y-auto rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-sm whitespace-pre-wrap"
          >
            {run.segments.map((seg, i) => (
              <span
                key={i}
                style={{ color: `var(--ledger-${seg.kind === "output" ? "output" : seg.kind})` }}
                className={seg.kind === "input" ? "border-b border-dashed border-zinc-300 block pb-2 mb-2" : ""}
              >
                {seg.text}
              </span>
            ))}
            {shouldShowWaitingAnimation(run.streaming, run.segments) && (
              <GolfAnimation />
            )}
            {run.streaming && !shouldShowWaitingAnimation(run.streaming, run.segments) && (
              <span className="animate-pulse">▌</span>
            )}
          </div>
        )}
        {run.runs.length > 0 && (
          <TokenLedger
            runs={buildRunBlocks(run.runs)}
          />
        )}
        {run.error && (
          <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{run.error}</p>
        )}
        <div className="flex gap-3">
          <button
            type="button"
            disabled={
              !selected ||
              run.streaming ||
              (selected !== null && run.runs.some((r) => r.optionId === selected.id))
            }
            onClick={practiceSwing}
            className="h-12 flex-1 rounded-full bg-green-700 font-medium text-white transition-colors hover:bg-green-800 disabled:opacity-40"
          >
            {run.streaming
              ? "Swinging…"
              : selected !== null && run.runs.some((r) => r.optionId === selected.id)
                ? "Already ran this option"
                : "Practice Swing"}
          </button>
          <button
            type="button"
            disabled={
              !selected ||
              run.streaming ||
              recording ||
              (selected !== null && !run.runs.some((r) => r.optionId === selected.id))
            }
            onClick={recordScore}
            className="h-12 flex-1 rounded-full border border-zinc-300 font-medium text-black transition-colors hover:bg-zinc-50 disabled:opacity-40"
          >
            {recording ? "Recording…" : "Record Score"}
          </button>
        </div>
      </div>
    </main>
  );
}
