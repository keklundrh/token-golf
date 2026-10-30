import { describe, it, expect } from "vitest";
import { computeCost, SPEND_CAP_USD, parseSpendCap, type TokenUsage } from "./cost";

const ORIGINAL_ENV = process.env.SPEND_CAP_USD;

function withEnv(value: string | undefined, run: () => void): void {
  if (value === undefined) {
    delete process.env.SPEND_CAP_USD;
  } else {
    process.env.SPEND_CAP_USD = value;
  }
  try {
    run();
  } finally {
    if (ORIGINAL_ENV === undefined) {
      delete process.env.SPEND_CAP_USD;
    } else {
      process.env.SPEND_CAP_USD = ORIGINAL_ENV;
    }
  }
}

describe("SPEND_CAP_USD parsing", () => {
  it("parses a valid override", () => {
    withEnv("0.75", () => {
      expect(parseSpendCap()).toBe(0.75);
    });
  });

  it("falls back to 0.5 on a non-numeric value", () => {
    withEnv("not-a-number", () => {
      expect(parseSpendCap()).toBe(0.5);
    });
  });

  it("falls back to 0.5 on a negative value", () => {
    withEnv("-1", () => {
      expect(parseSpendCap()).toBe(0.5);
    });
  });

  it("defaults to 0.5 when absent", () => {
    withEnv(undefined, () => {
      expect(parseSpendCap()).toBe(0.5);
    });
  });
});
const usage: TokenUsage = {
  inputTokens: 1_000_000,
  outputTokens: 100_000,
  reasoningTokens: 10_000,
};

describe("computeCost", () => {
  it("computes per-category costs from real pricing config", () => {
    // openai/gpt-5-mini: input 0.25, output 2.00, reasoning null
    const cost = computeCost("openai/gpt-5-mini", {
      inputTokens: 1_000_000,
      outputTokens: 100_000,
      reasoningTokens: null,
    });
    expect(cost.inputUsd).toBeCloseTo(0.25);
    expect(cost.outputUsd).toBeCloseTo(0.2);
    expect(cost.reasoningUsd).toBe(0);
    expect(cost.totalUsd).toBeCloseTo(0.45);
  });

  it("prices reasoning tokens when the model reports them", () => {
    // anthropic/claude-sonnet-4-5: input 3.00, output 15.00, reasoning 15.00
    const cost = computeCost("anthropic/claude-sonnet-4-5", {
      inputTokens: 100_000,
      outputTokens: 10_000,
      reasoningTokens: 1_000,
    });
    expect(cost.inputUsd).toBeCloseTo(0.3);
    expect(cost.outputUsd).toBeCloseTo(0.15);
    expect(cost.reasoningUsd).toBeCloseTo(0.015);
    expect(cost.totalUsd).toBeCloseTo(0.465);
  });

  it("treats null reasoning tokens as zero cost", () => {
    const cost = computeCost("anthropic/claude-sonnet-4-5", {
      inputTokens: 1_000,
      outputTokens: 1_000,
      reasoningTokens: null,
    });
    expect(cost.reasoningUsd).toBe(0);
  });

  it("throws on unknown model", () => {
    expect(() =>
      computeCost("unknown/model", { inputTokens: 1, outputTokens: 1, reasoningTokens: null }),
    ).toThrow("no pricing for model");
  });


  it("prices cache reads and writes with provider-specific rates without double-charging", () => {
    // inputTokens includes cached tokens (SDK semantics);
    // anthropic/claude-sonnet-4-5: input 3.00, output 15.00, read 0.30, write 3.75
    const cost = computeCost("anthropic/claude-sonnet-4-5", {
      inputTokens: 100_000, // 30k uncached + 50k read + 20k write
      outputTokens: 10_000,
      reasoningTokens: null,
      cacheReadTokens: 50_000,
      cacheWriteTokens: 20_000,
    });
    expect(cost.cacheReadUsd).toBeCloseTo(0.015); // 50_000/1e6 * 0.30
    expect(cost.cacheWriteUsd).toBeCloseTo(0.075); // 20_000/1e6 * 3.75
    expect(cost.inputUsd).toBeCloseTo(0.09); // 30_000/1e6 * 3.00 — only the uncached remainder
    expect(cost.outputUsd).toBeCloseTo(0.15);
    expect(cost.totalUsd).toBeCloseTo(0.33);
  });

  it("keeps the total covering all tokens when cache pricing is absent", () => {
    // openai/gpt-5-mini has no cache rates: cached tokens fall back to the
    // input rate, so the total equals full input + output
    const cost = computeCost("openai/gpt-5-mini", {
      inputTokens: 1_000_000,
      outputTokens: 1_000,
      reasoningTokens: null,
      cacheReadTokens: 500_000,
      cacheWriteTokens: 500_000,
    });
    expect(cost.cacheReadUsd).toBe(0);
    expect(cost.cacheWriteUsd).toBe(0);
    expect(cost.totalUsd).toBeCloseTo(0.25 + 0.002); // full input + output
  });

  it("contributes zero cache cost when the SDK reports no cache tokens", () => {
    const cost = computeCost("anthropic/claude-sonnet-4-5", {
      inputTokens: 1_000,
      outputTokens: 1_000,
      reasoningTokens: null,
      cacheReadTokens: null,
      cacheWriteTokens: null,
    });
    expect(cost.cacheReadUsd).toBe(0);
    expect(cost.cacheWriteUsd).toBe(0);
  });

  it("contributes zero cache cost when pricing lacks cache rates", () => {
    const cost = computeCost("openai/gpt-5-mini", {
      inputTokens: 1_000_000,
      outputTokens: 1_000,
      reasoningTokens: null,
      cacheReadTokens: 500_000,
      cacheWriteTokens: 500_000,
    });
    expect(cost.cacheReadUsd).toBe(0);
    expect(cost.cacheWriteUsd).toBe(0);
  });
});

describe("SPEND_CAP_USD", () => {
  it("defaults to 0.50", () => {
    expect(SPEND_CAP_USD).toBe(0.5);
  });
});

