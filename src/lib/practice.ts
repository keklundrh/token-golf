import type { Challenge, Option } from "@/lib/config";
import { renderPrompt, modelFor } from "@/lib/llm";
import { streamText } from "ai";

export interface PracticeEvent {
  type: "chunk" | "done";
  text?: string;
}

export function renderPracticeStream({
  challenge,
  option,
}: {
  challenge: Challenge;
  option: Option;
}): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    async start(controller) {
      const model = modelFor(challenge.model);
      const result = streamText({
        model,
        prompt: renderPrompt(option, challenge.question),
      });
      for await (const chunk of result.textStream) {
        const event: PracticeEvent = { type: "chunk", text: chunk };
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
      }
      const done: PracticeEvent = { type: "done" };
      controller.enqueue(encoder.encode(`data: ${JSON.stringify(done)}\n\n`));
      controller.close();
    },
  });
}
