import type { Challenge, Option, Skills } from "@/lib/config";
import { renderPrompt, modelFor } from "@/lib/llm";
import { streamText } from "ai";
import { computeCost } from "@/lib/cost";

export type ChunkKind = "input" | "output" | "reasoning" | "tools";

export interface PracticeEvent {
  type: "chunk" | "done";
  text?: string;
  kind?: ChunkKind;
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
}

export function renderPracticeStream({
  challenge,
  option,
  skills,
}: {
  challenge: Challenge;
  option: Option;
  skills: Skills;
}): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    async start(controller) {
      const model = modelFor(option.model ?? challenge.model);
      const renderedPrompt = renderPrompt(option, challenge.question, skills);
      const result = streamText({
        model,
        prompt: renderedPrompt,
        ...(option.thinking
          ? {
              providerOptions: {
                anthropic: {
                  thinking: { type: "enabled" as const, budgetTokens: 4096 },
                },
              },
            }
          : {}),
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
      };
      const cost = computeCost(option.model ?? challenge.model, tokens);
      const done: PracticeEvent = {
        type: "done",
        usage: {
          ...tokens,
          toolTokens: 0,
          toolCalls: toolCalls.length,
          inputUsd: cost.inputUsd,
          outputUsd: cost.outputUsd,
          reasoningUsd: cost.reasoningUsd,
          costUsd: cost.totalUsd,
        },
      };
      controller.enqueue(encoder.encode(`data: ${JSON.stringify(done)}\n\n`));
      controller.close();
    },
  });
}
