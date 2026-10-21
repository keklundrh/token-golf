import { describe, it, expect, vi, beforeEach } from "vitest";
import { loadChallenge, loadSkills, type Skills } from "./config";

const streamTextMock = vi.hoisted(() => vi.fn());

vi.mock("ai", () => ({
  streamText: streamTextMock,
}));

vi.mock("@ai-sdk/openai", () => ({
  createOpenAI: () => (id: string) => ({ provider: "openai", modelId: id }),
}));

vi.mock("@ai-sdk/anthropic", () => ({
  createAnthropic: () => (id: string) => ({ provider: "anthropic", modelId: id }),
}));

import { renderPracticeStream } from "./practice";

const skills: Skills = loadSkills();

async function drain(stream: ReadableStream<Uint8Array>): Promise<string> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let out = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) return out;
    out += decoder.decode(value, { stream: true });
  }
}

describe("renderPracticeStream streamText args", () => {
  beforeEach(() => {
    streamTextMock.mockReset();
    streamTextMock.mockReturnValue({
      fullStream: (async function* () {
        yield { type: "text-delta", text: "ok" };
      })(),
      usage: Promise.resolve({
        inputTokens: 1,
        outputTokens: 1,
        outputTokenDetails: { reasoningTokens: undefined },
      }),
      toolCalls: Promise.resolve([]),
    });
  });

  it("resolves option-level model over hole default", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], model: "anthropic/claude-haiku-4-5" };
    await drain(renderPracticeStream({ challenge, option, skills }));
    expect(streamTextMock).toHaveBeenCalledTimes(1);
    expect(streamTextMock.mock.calls[0][0].model.modelId).toBe("claude-haiku-4-5");
  });

  it("uses hole default model when option has none", async () => {
    const challenge = loadChallenge(1);
    await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills }));
    expect(streamTextMock.mock.calls[0][0].model.modelId).toBe("claude-sonnet-4-5");
  });

  it("passes thinking enabled with budgetTokens when option.thinking is set", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], thinking: true };
    await drain(renderPracticeStream({ challenge, option, skills }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.providerOptions).toEqual({
      anthropic: { thinking: { type: "enabled", budgetTokens: 4096 } },
    });
  });

  it("passes no providerOptions when thinking is unset", async () => {
    const challenge = loadChallenge(1);
    await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.providerOptions).toBeUndefined();
  });

  it("prepends skill prompts before the option prompt", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], skills: ["web-search"] };
    await drain(renderPracticeStream({ challenge, option, skills }));
    const prompt: string = streamTextMock.mock.calls[0][0].prompt;
    expect(prompt.indexOf("Search the web")).toBeLessThan(
      prompt.indexOf("You are a thorough science teacher"),
    );
  });

  it("emits done frame with tool call count and per-category costs", async () => {
    const challenge = loadChallenge(1);
    const events: string[] = [];
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills }));
    for (const frame of raw.split("\n\n")) {
      if (frame.startsWith("data: ")) events.push(frame.slice(6));
    }
    const done = JSON.parse(events[events.length - 1]);
    expect(done.type).toBe("done");
    expect(done.usage.toolCalls).toBe(0);
    expect(done.usage.inputUsd).toBeTypeOf("number");
    expect(done.usage.costUsd).toBeGreaterThan(0);
  });
});
