import { describe, it, expect, vi, beforeEach } from "vitest";
import { loadChallenge, loadSkills, type Skills } from "./config";

const streamTextMock = vi.hoisted(() => vi.fn());

const TEST_USER_ID = "practice-test-user";
const insertValuesMock = vi.hoisted(() => vi.fn(() => ({ run: vi.fn() })));
const insertMock = vi.hoisted(() => vi.fn(() => ({ values: insertValuesMock })));

vi.mock("@/db", () => ({
  getDb: () => ({ insert: insertMock }),
}));

vi.mock("ai", () => ({
  streamText: streamTextMock,
}));

vi.mock("@ai-sdk/openai", () => ({
  createOpenAI: () => (id: string) => ({ provider: "openai", modelId: id }),
}));

vi.mock("@ai-sdk/anthropic", () => ({
  createAnthropic: () => (id: string) => ({ provider: "anthropic", modelId: id }),
}));

vi.mock("@ai-sdk/openai-compatible", () => ({
  createOpenAICompatible:
    (config: { name: string }) => (id: string) => ({
      provider: config.name,
      modelId: id,
    }),
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
    insertMock.mockClear();
    insertValuesMock.mockClear();
    insertValuesMock.mockImplementation(() => ({ run: vi.fn() }));
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
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    expect(streamTextMock).toHaveBeenCalledTimes(1);
    expect(streamTextMock.mock.calls[0][0].model.modelId).toBe("claude-haiku-4-5");
  });

  it("uses hole default model when option has none", async () => {
    const challenge = loadChallenge(1);
    await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills, userId: TEST_USER_ID }));
    expect(streamTextMock.mock.calls[0][0].model.modelId).toBe("claude-sonnet-4-5");
  });

  it("passes Anthropic thinking enabled with budgetTokens 4096 when option.thinking is true", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], thinking: true };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.providerOptions).toEqual({
      anthropic: { thinking: { type: "enabled", budgetTokens: 4096 } },
    });
  });

  it("passes no providerOptions when thinking is unset", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], thinking: undefined };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.providerOptions).toBeUndefined();
  });

  it("maps thinking low to Anthropic budget 2048", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], thinking: "low" as const };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
      anthropic: { thinking: { type: "enabled", budgetTokens: 2048 } },
    });
  });

  it("maps thinking high to Anthropic budget 8192", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], thinking: "high" as const };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
      anthropic: { thinking: { type: "enabled", budgetTokens: 8192 } },
    });
  });

  it("passes OpenAI reasoningEffort for graded thinking on an openai model", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], model: "openai/gpt-5-mini", thinking: "high" as const };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
      openai: { reasoningEffort: "high" },
    });
  });

  it("maps thinking true to OpenAI reasoningEffort medium", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], model: "openai/gpt-5-mini", thinking: true as const };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
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
      await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
      expect(streamTextMock.mock.calls[0][0].providerOptions).toEqual({
        anthropic: { thinking: { type: "enabled", budgetTokens: budget } },
      });
      streamTextMock.mockClear();
    }
  });

  it("prepends skill prompts before the option prompt", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], skills: ["web-search"] };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const prompt: string = streamTextMock.mock.calls[0][0].prompt;
    // skills come first; the option's own prompt (question substituted) follows
    expect(prompt.indexOf("Search the web")).toBeLessThan(
      prompt.indexOf(challenge.question),
    );
  });

  it("emits input chunk first with the rendered prompt", async () => {
    const challenge = loadChallenge(1);
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills, userId: TEST_USER_ID }));
    const frames = raw.split("\n\n").filter((f) => f.startsWith("data: "));
    const first = JSON.parse(frames[0].slice(6));
    expect(first.type).toBe("chunk");
    expect(first.kind).toBe("input");
    expect(first.text).toContain(challenge.question);
  });

  it("tags text-delta chunks as output kind", async () => {
    const challenge = loadChallenge(1);
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills, userId: TEST_USER_ID }));
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
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills, userId: TEST_USER_ID }));
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
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills, userId: TEST_USER_ID }));
    const frames = raw.split("\n\n").filter((f) => f.startsWith("data: "));
    const toolFrame = JSON.parse(frames[1].slice(6));
    expect(toolFrame.kind).toBe("tools");
    expect(toolFrame.text).toBe("calling tool…");
    expect(toolFrame.text).not.toContain("{");
  });

  it("emits done frame with tool call count and per-category costs", async () => {
    const challenge = loadChallenge(1);
    const events: string[] = [];
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills, userId: TEST_USER_ID }));
    for (const frame of raw.split("\n\n")) {
      if (frame.startsWith("data: ")) events.push(frame.slice(6));
    }
    const done = JSON.parse(events[events.length - 1]);
    expect(done.type).toBe("done");
    expect(done.usage.toolCalls).toBe(0);
    expect(done.usage.inputUsd).toBeTypeOf("number");
    expect(done.usage.costUsd).toBeGreaterThan(0);
  });



  it("sends no cache metadata when caching is off", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], caching: false };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.prompt).toBeDefined();
    expect(args.messages).toBeUndefined();
  });

  it("puts Anthropic cacheControl on the prompt block's providerOptions", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], caching: true };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.prompt).toBeUndefined();
    expect(args.messages).toEqual([
      {
        role: "user",
        content: [
          {
            type: "text",
            text: expect.any(String),
            providerOptions: { anthropic: { cacheControl: { type: "ephemeral" } } },
          },
        ],
      },
    ]);
  });

  it("puts OpenAI promptCacheBreakpoint on the prompt block's providerOptions", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], model: "openai/gpt-5-mini", caching: true };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.messages).toEqual([
      {
        role: "user",
        content: [
          {
            type: "text",
            text: expect.any(String),
            providerOptions: { openai: { promptCacheBreakpoint: true } },
          },
        ],
      },
    ]);
  });

  it("sends plain prompt for openai-compatible endpoints with caching on", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], model: "ai-bu-cai/Qwen3.8-27B", caching: true };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.prompt).toBeDefined();
    expect(args.messages).toBeUndefined();
  });

  it("keeps thinking at call level and cache on the prompt block", async () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], thinking: "low" as const, caching: true };
    await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const args = streamTextMock.mock.calls[0][0];
    expect(args.providerOptions).toEqual({
      anthropic: { thinking: { type: "enabled", budgetTokens: 2048 } },
    });
    expect(args.messages[0].content[0].providerOptions).toEqual({
      anthropic: { cacheControl: { type: "ephemeral" } },
    });
  });

  it("emits done frame cache fields from inputTokenDetails", async () => {
    streamTextMock.mockReturnValue({
      fullStream: (async function* () {
        yield { type: "text-delta", text: "ok" };
      })(),
      usage: Promise.resolve({
        inputTokens: 100_000,
        outputTokens: 10_000,
        outputTokenDetails: { reasoningTokens: undefined },
        inputTokenDetails: { cacheReadTokens: 50_000, cacheWriteTokens: 20_000 },
      }),
      toolCalls: Promise.resolve([]),
    });
    const challenge = loadChallenge(1);
    // anthropic/claude-sonnet-4-5: input 3.00, output 15.00, cache read 0.30,
    // cache write 3.75 — inputTokens includes cached tokens, so uncached is 30k
    const option = { ...challenge.options[0], model: "anthropic/claude-sonnet-4-5", caching: true };
    const raw = await drain(renderPracticeStream({ challenge, option, skills, userId: TEST_USER_ID }));
    const frames = raw.split("\n\n").filter((f) => f.startsWith("data: "));
    const done = JSON.parse(frames[frames.length - 1].slice(6));
    expect(done.usage.cacheReadTokens).toBe(50_000);
    expect(done.usage.cacheWriteTokens).toBe(20_000);
    expect(done.usage.cacheReadUsd).toBeCloseTo(0.015); // 50_000/1e6 * 0.30
    expect(done.usage.cacheWriteUsd).toBeCloseTo(0.075); // 20_000/1e6 * 3.75
    // total = uncached 30k*3 + read + write + output 10k*15; no double-charge
    expect(done.usage.costUsd).toBeCloseTo(0.09 + 0.015 + 0.075 + 0.15);
  });

  it("emits null cache fields when the SDK reports no cache details", async () => {
    const challenge = loadChallenge(1);
    const raw = await drain(renderPracticeStream({ challenge, option: challenge.options[0], skills, userId: TEST_USER_ID }));
    const frames = raw.split("\n\n").filter((f) => f.startsWith("data: "));
    const done = JSON.parse(frames[frames.length - 1].slice(6));
    expect(done.usage.cacheReadTokens).toBeNull();
    expect(done.usage.cacheWriteTokens).toBeNull();
    expect(done.usage.cacheReadUsd).toBe(0);
    expect(done.usage.cacheWriteUsd).toBe(0);
  });
});
