import { describe, it, expect } from "vitest";
import { computeCost, SPEND_CAP_USD, type TokenUsage } from "./cost";

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
});

describe("SPEND_CAP_USD", () => {
  it("defaults to 0.50", () => {
    expect(SPEND_CAP_USD).toBe(0.5);
  });
});
