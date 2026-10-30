import type { Challenge, Option, Skills } from "@/lib/config";
import { renderPrompt, modelFor } from "@/lib/llm";
import { streamText, type JSONValue } from "ai";
import { computeCost } from "@/lib/cost";
import { getDb } from "@/db";
import { attempts } from "@/db/schema";

export type ChunkKind = "input" | "output" | "reasoning" | "tools";

/** Anthropic has no native effort knob: graded modes map to budget tiers. */
const ANTHROPIC_BUDGET: Record<"low" | "medium" | "high", number> = {
  low: 2048,
  medium: 4096,
  high: 8192,
};


export function effortProviderOptions(
  thinking: Option["thinking"],
  modelSpec: string,
): Record<string, Record<string, JSONValue>> | undefined {
  const provider = modelSpec.split("/")[0];
  if (!thinking) return undefined;
  if (provider.startsWith("openai")) {
    const effort = thinking === true ? "medium" : thinking;
    return { openai: { reasoningEffort: effort } };
  }
  const budgetTokens = thinking === true ? 4096 : ANTHROPIC_BUDGET[thinking];
  return { anthropic: { thinking: { type: "enabled" as const, budgetTokens } } };
}

/**
 * Cache wiring per provider. Anthropic: cache_control on the prompt block
 * (cacheable on user message parts, applied at the last part). OpenAI:
 * promptCacheBreakpoint. OpenAI-compatible endpoints (ai-bu-*) have no
 * cache-control wire format — the flag is a no-op there; usage still reports
 * cache tokens when the backend serves them.
 */
export function cacheProviderOptions(
  caching: Option["caching"],
  modelSpec: string,
): Record<string, Record<string, JSONValue>> | undefined {
  if (!caching) return undefined;
  const provider = modelSpec.split("/")[0];
  if (provider.startsWith("openai")) {
    return { openai: { promptCacheBreakpoint: true } };
  }
  if (provider.startsWith("anthropic")) {
    return { anthropic: { cacheControl: { type: "ephemeral" as const } } };
  }
  return undefined;
}

export interface PracticeEvent {
  type: "chunk" | "done";
  text?: string;
  kind?: ChunkKind;
  usage?: {
    inputTokens: number;
    outputTokens: number;
    reasoningTokens: number | null;
    cacheReadTokens: number | null;
    cacheWriteTokens: number | null;
    toolTokens: number;
    toolCalls: number;
    inputUsd: number;
    outputUsd: number;
    reasoningUsd: number;
    cacheReadUsd: number;
    cacheWriteUsd: number;
    costUsd: number;
  };
}

export function renderPracticeStream({
  challenge,
  option,
  skills,
  userId,
}: {
  challenge: Challenge;
  option: Option;
  skills: Skills;
  userId: string;
}): ReadableStream<Uint8Array> {
  return new ReadableStream<Uint8Array>({
    async start(controller) {
      const encoder = new TextEncoder();
      const modelSpec = option.model ?? challenge.model;
      const model = modelFor(modelSpec);
      const renderedPrompt = renderPrompt(option, challenge.question, skills, userId);
      const providerOptions = effortProviderOptions(option.thinking, modelSpec);
      // Cache metadata must ride on the prompt BLOCK's providerOptions — both
      // providers read it per message (Anthropic CacheControlValidator pulls
      // cacheControl from part/message providerOptions; OpenAI
      // getPromptCacheBreakpoint reads the prompt block's providerOptions).
      // Call-level providerOptions never reaches the wire for caching.
      const cacheOptions = cacheProviderOptions(option.caching, modelSpec);
      const result = streamText({
        model,
        ...(cacheOptions
          ? {
              messages: [
                {
                  role: "user" as const,
                  content: [{ type: "text" as const, text: renderedPrompt, providerOptions: cacheOptions }],
                },
              ],
            }
          : { prompt: renderedPrompt }),
        ...(providerOptions ? { providerOptions } : {}),
      });
      const inputEvent: PracticeEvent = { type: "chunk", text: renderedPrompt, kind: "input" };
      controller.enqueue(encoder.encode(`data: ${JSON.stringify(inputEvent)}\n\n`));
      for await (const part of result.fullStream) {
        if (part.type === "text-delta") {
          const event: PracticeEvent = { type: "chunk", text: part.text, kind: "output" };
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
        } else if (part.type === "reasoning-delta") {
          const event: PracticeEvent = { type: "chunk", text: part.text, kind: "reasoning" };
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
        } else if (part.type === "tool-call") {
          const event: PracticeEvent = { type: "chunk", text: "calling tool…", kind: "tools" };
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
        }
      }
      const usage = await result.usage;
      const toolCalls = await result.toolCalls;
      const tokens = {
        inputTokens: usage.inputTokens ?? 0,
        outputTokens: usage.outputTokens ?? 0,
        reasoningTokens: usage.outputTokenDetails?.reasoningTokens ?? null,
        cacheReadTokens: usage.inputTokenDetails?.cacheReadTokens ?? null,
        cacheWriteTokens: usage.inputTokenDetails?.cacheWriteTokens ?? null,
      };
      const cost = computeCost(option.model ?? challenge.model, tokens);
      // server-side run tracking: the proxy measured this cost, so the server
      // records the attempt (#7 invariant — the client never self-reports cost)
      getDb()
        .insert(attempts)
        .values({
          userId,
          challengeId: challenge.id,
          optionId: option.id,
          costUsd: cost.totalUsd,
          inputTokens: tokens.inputTokens,
          outputTokens: tokens.outputTokens,
          reasoningTokens: tokens.reasoningTokens,
          cacheReadTokens: tokens.cacheReadTokens,
          cacheWriteTokens: tokens.cacheWriteTokens,
          createdAt: Date.now(),
        })
        .run();
      const done: PracticeEvent = {
        type: "done",
        usage: {
          ...tokens,
          toolTokens: 0,
          toolCalls: toolCalls.length,
          inputUsd: cost.inputUsd,
          outputUsd: cost.outputUsd,
          reasoningUsd: cost.reasoningUsd,
          cacheReadUsd: cost.cacheReadUsd,
          cacheWriteUsd: cost.cacheWriteUsd,
          costUsd: cost.totalUsd,
        },
      };
      controller.enqueue(encoder.encode(`data: ${JSON.stringify(done)}\n\n`));
      controller.close();
    },
  });
}
