"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { Challenge, Option } from "@/lib/config";
import TokenLedger from "./token-ledger";
import { buildLedger } from "@/lib/ledger";

export interface ChallengeViewProps {
  challenge: Challenge;
  holeCount: number;
}

interface RunState {
  output: string;
  streaming: boolean;
  error: string | null;
  costUsd: number | null;
  usage: {
    inputTokens: number;
    outputTokens: number;
    reasoningTokens: number | null;
    toolTokens: number;
    toolCalls: number;
    inputUsd: number;
    outputUsd: number;
    reasoningUsd: number;
  } | null;
}

export default function ChallengeView({ challenge, holeCount }: ChallengeViewProps) {
  const [selected, setSelected] = useState<Option | null>(null);
  const [run, setRun] = useState<RunState>({
    output: "",
    streaming: false,
    error: null,
    costUsd: null,
    usage: null,
  });
  const [recording, setRecording] = useState(false);
  const router = useRouter();
  const outputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSelected(null);
    setRun({ output: "", streaming: false, error: null, costUsd: null, usage: null });
    setRecording(false);
  }, [challenge.id]);

  useEffect(() => {
    if (run.streaming && outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [run.output, run.streaming]);

  function practiceSwing() {
    if (!selected || run.streaming) return;
    setRun({ output: "", streaming: true, error: null, costUsd: null, usage: null });

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
              setRun((r) => ({ ...r, output: r.output + event.text }));
            } else if (event.type === "done" && event.usage) {
              setRun((r) => ({
                ...r,
                costUsd: event.usage!.costUsd,
                usage: {
                  inputTokens: event.usage!.inputTokens,
                  outputTokens: event.usage!.outputTokens,
                  reasoningTokens: event.usage!.reasoningTokens,
                  toolTokens: event.usage!.toolTokens,
                  toolCalls: event.usage!.toolCalls,
                  inputUsd: event.usage!.inputUsd,
                  outputUsd: event.usage!.outputUsd,
                  reasoningUsd: event.usage!.reasoningUsd,
                },
              }));
            }
          }
        }
        setRun((r) => ({ ...r, streaming: false }));
      })
      .catch((e: Error) =>
        setRun({ output: "", streaming: false, error: e.message, costUsd: null, usage: null }),
      );
  }

  function recordScore() {
    if (!selected || recording || run.costUsd === null) return;
    setRecording(true);
    fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ challengeId: challenge.id, costUsd: run.costUsd }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`record failed: ${res.status}`);
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
            Hole {challenge.id} / {holeCount} · Par {challenge.par}
          </p>
          <p className="text-sm text-zinc-500">
            {run.costUsd !== null
              ? `Spend $${run.costUsd.toFixed(4)}`
              : "Spend $0.00"}
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
            </button>
          ))}
        </div>
        {run.output.length > 0 && (
          <div
            ref={outputRef}
            className="max-h-64 overflow-y-auto rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-sm whitespace-pre-wrap"
          >
            {run.output}
            {run.streaming && <span className="animate-pulse">▌</span>}
          </div>
        )}
        {run.costUsd !== null && run.usage && (
          <TokenLedger {...buildLedger(run.usage, {
            inputUsd: run.usage.inputUsd,
            outputUsd: run.usage.outputUsd,
            reasoningUsd: run.usage.reasoningUsd,
            totalUsd: run.costUsd,
          })} />
        )}
        {run.error && (
          <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{run.error}</p>
        )}
        <div className="flex gap-3">
          <button
            type="button"
            disabled={!selected || run.streaming}
            onClick={practiceSwing}
            className="h-12 flex-1 rounded-full bg-green-700 font-medium text-white transition-colors hover:bg-green-800 disabled:opacity-40"
          >
            {run.streaming ? "Swinging…" : "Practice Swing"}
          </button>
          <button
            type="button"
            disabled={!selected || run.streaming || run.output.length === 0 || recording}
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
