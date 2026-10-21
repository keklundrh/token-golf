import type { Challenge, Option, Skills } from "@/lib/config";
import { renderPrompt, modelFor } from "@/lib/llm";
import { streamText } from "ai";
import { computeCost } from "@/lib/cost";

export interface PracticeEvent {
  type: "chunk" | "done";
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
      const result = streamText({
        model,
        prompt: renderPrompt(option, challenge.question, skills),
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
      for await (const chunk of result.textStream) {
        const event: PracticeEvent = { type: "chunk", text: chunk };
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
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
