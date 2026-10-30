import { describe, it, expect } from "vitest";
import { buildRunTip } from "./tips";

const base = {
  optionLabel: "Detailed explanation",
  modelId: "anthropic/claude-sonnet-4-5",
  rates: { inputPerMtok: 3, outputPerMtok: 15, reasoningPerMtok: 15 },
};

describe("buildRunTip", () => {
  it("names the option, model, and dominant category with its rate", () => {
    const tip = buildRunTip({
      ...base,
      usage: { inputTokens: 29, outputTokens: 300, reasoningTokens: null },
      costs: { inputUsd: 0.000087, outputUsd: 0.0045, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0 },
    });
    expect(tip).toContain("Detailed explanation");
    expect(tip).toContain("anthropic/claude-sonnet-4-5");
    expect(tip).toContain("output");
    expect(tip).toContain("300 tok at 15 µ$/tok");
  });

  it("derives the suggestion from the dominant category — never invents one", () => {
    const outputDominated = buildRunTip({
      ...base,
      usage: { inputTokens: 29, outputTokens: 300, reasoningTokens: null },
      costs: { inputUsd: 0.000087, outputUsd: 0.0045, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0 },
    });
    expect(outputDominated).toContain("shorter output");

    const thinkingDominated = buildRunTip({
      ...base,
      usage: { inputTokens: 29, outputTokens: 30, reasoningTokens: 220 },
      costs: { inputUsd: 0.000087, outputUsd: 0.00045, reasoningUsd: 0.0033, cacheReadUsd: 0, cacheWriteUsd: 0 },
      flags: { thinking: true },
    });
    expect(thinkingDominated).toContain("thinking");

    const inputDominated = buildRunTip({
      ...base,
      usage: { inputTokens: 1_035, outputTokens: 30, reasoningTokens: null },
      costs: { inputUsd: 0.003105, outputUsd: 0.00045, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0 },
    });
    expect(inputDominated).toContain("input");
  });

  it("treats a cache write as the dominant cost when it is", () => {
    const tip = buildRunTip({
      ...base,
      usage: { inputTokens: 10_000, outputTokens: 30, reasoningTokens: null, cacheWriteTokens: 9_500 },
      costs: { inputUsd: 0.00015, outputUsd: 0.00045, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0.035625 },
      flags: { caching: true },
    });
    expect(tip).toContain("cache write");
    expect(tip).toContain("cheaper on the next equivalent run");
  });

  it("renders thinking tokens at their own rate when reasoning dominates", () => {
    const tip = buildRunTip({
      ...base,
      usage: { inputTokens: 29, outputTokens: 30, reasoningTokens: 220 },
      costs: { inputUsd: 0.000087, outputUsd: 0.00045, reasoningUsd: 0.0033, cacheReadUsd: 0, cacheWriteUsd: 0 },
      flags: { thinking: true },
    });
    expect(tip).toContain("220 tok at 15 µ$/tok");
  });

  it("renders cache read tokens at the read rate from real config rates", () => {
    const tip = buildRunTip({
      ...base,
      rates: { inputPerMtok: 3, outputPerMtok: 15, reasoningPerMtok: 15, cacheReadPerMtok: 0.3, cacheWritePerMtok: 3.75 },
      usage: { inputTokens: 50_000, outputTokens: 30, reasoningTokens: null, cacheReadTokens: 49_000 },
      costs: { inputUsd: 0.00003, outputUsd: 0.00045, reasoningUsd: 0, cacheReadUsd: 0.0147, cacheWriteUsd: 0 },
      flags: { caching: true },
    });
    expect(tip).toContain("cache read");
    expect(tip).toContain("49,000 tok at 0.3 µ$/tok");
  });

  it("ignores reported reasoning/cache tokens without the flag — same rule as the ledger", () => {
    const tip = buildRunTip({
      ...base,
      usage: { inputTokens: 29, outputTokens: 30, reasoningTokens: 71, cacheReadTokens: 49_000, cacheWriteTokens: 20_000 },
      costs: { inputUsd: 0.000087, outputUsd: 0.00045, reasoningUsd: 0, cacheReadUsd: 0.0147, cacheWriteUsd: 0.075 },
      // no flags: reasoning reported (endpoint default) but not requested
    });
    expect(tip).toContain("output tokens dominated");
    expect(tip).not.toContain("thinking");
    expect(tip).not.toContain("cache");
  });
});
