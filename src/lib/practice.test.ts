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

  it("passes Anthropic thinking enabled with budgetTokens 4096 when option.thinking is true", async () => {
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
    const option = { ...challenge.options[0], thinking: undefined };
    await drain(renderPracticeStream({ challenge, option, skills }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.providerOptions).toBeUndefined();
  });

  it("maps thinking low to Anthropic budget 2048", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], thinking: "low" as const };
    await drain(renderPracticeStream({ challenge, option, skills }));
    expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
      anthropic: { thinking: { type: "enabled", budgetTokens: 2048 } },
    });
  });

  it("maps thinking high to Anthropic budget 8192", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], thinking: "high" as const };
    await drain(renderPracticeStream({ challenge, option, skills }));
    expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
      anthropic: { thinking: { type: "enabled", budgetTokens: 8192 } },
    });
  });

  it("passes OpenAI reasoningEffort for graded thinking on an openai model", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], model: "openai/gpt-5-mini", thinking: "high" as const };
    await drain(renderPracticeStream({ challenge, option, skills }));
    expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
      openai: { reasoningEffort: "high" },
    });
  });

  it("maps thinking true to OpenAI reasoningEffort medium", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], model: "openai/gpt-5-mini", thinking: true as const };
    await drain(renderPracticeStream({ challenge, option, skills }));
    expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
      openai: { reasoningEffort: "medium" },
    });
  });

  it("maps graded Anthropic budgets low, medium, high via the budget table", async () => {
    const challenge = loadChallenge(1);
    const cases = [
      { mode: "low", budget: 2048 },
      { mode: "medium", budget: 4096 },
      { mode: "high", budget: 8192 },
    ] as const;
    for (const { mode, budget } of cases) {
      const option = { ...challenge.options[0], thinking: mode };
      await drain(renderPracticeStream({ challenge, option, skills }));
      expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
        anthropic: { thinking: { type: "enabled", budgetTokens: budget } },
      });
      streamTextMock.mockClear();
    }
  });

  it("prepends skill prompts before the option prompt", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], skills: ["web-search"] };
    await drain(renderPracticeStream({ challenge, option, skills }));
    const prompt: string = streamTextMock.mock.calls[0][0].prompt;
    // skills come first; the option's own prompt (question substituted) follows
    expect(prompt.indexOf("Search the web")).toBeLessThan(
      prompt.indexOf(challenge.question),
    );
  });

  it("emits input chunk first with the rendered prompt", async () => {
    const challenge = loadChallenge(1);
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills }));
    const frames = raw.split("\n\n").filter((f) => f.startsWith("data: "));
    const first = JSON.parse(frames[0].slice(6));
    expect(first.type).toBe("chunk");
    expect(first.kind).toBe("input");
    expect(first.text).toContain("Why is the sky blue");
  });

  it("tags text-delta chunks as output kind", async () => {
    const challenge = loadChallenge(1);
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills }));
    const kinds = raw.split("\n\n").filter((f) => f.startsWith("data: ")).map((f) => JSON.parse(f.slice(6)).kind);
    expect(kinds[0]).toBe("input");
    expect(kinds[1]).toBe("output");
  });

  it("tags reasoning-delta chunks as reasoning kind", async () => {
    streamTextMock.mockReset();
    streamTextMock.mockReturnValue({
      fullStream: (async function* () {
        yield { type: "reasoning-delta", text: "thinking..." };
        yield { type: "text-delta", text: "answer" };
      })(),
      usage: Promise.resolve({
        inputTokens: 1,
        outputTokens: 1,
        outputTokenDetails: { reasoningTokens: undefined },
      }),
      toolCalls: Promise.resolve([]),
    });
    const challenge = loadChallenge(1);
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills }));
    const kinds = raw.split("\n\n").filter((f) => f.startsWith("data: ")).map((f) => JSON.parse(f.slice(6))).filter((e) => e.type === "chunk").map((e) => e.kind);
    expect(kinds).toEqual(["input", "reasoning", "output"]);
  });

  it("tags tool-call parts as tools kind without raw JSON", async () => {
    streamTextMock.mockReset();
    streamTextMock.mockReturnValue({
      fullStream: (async function* () {
        yield { type: "tool-call", toolCallId: "t1", toolName: "web-search", input: { q: "x" } };
      })(),
      usage: Promise.resolve({
        inputTokens: 1,
        outputTokens: 1,
        outputTokenDetails: { reasoningTokens: undefined },
      }),
      toolCalls: Promise.resolve([]),
    });
    const challenge = loadChallenge(1);
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills }));
    const frames = raw.split("\n\n").filter((f) => f.startsWith("data: "));
    const toolFrame = JSON.parse(frames[1].slice(6));
    expect(toolFrame.kind).toBe("tools");
    expect(toolFrame.text).toBe("calling tool…");
    expect(toolFrame.text).not.toContain("{");
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
