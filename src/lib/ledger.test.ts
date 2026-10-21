import { describe, it, expect } from "vitest";
import { buildLedger } from "./ledger";
import type { TokenUsage } from "./cost";

const baseUsage: TokenUsage & { toolTokens: number; toolCalls: number } = {
  inputTokens: 100,
  outputTokens: 200,
  reasoningTokens: null,
  toolTokens: 0,
  toolCalls: 0,
};

const baseCosts = {
  inputUsd: 0.000025,
  outputUsd: 0.0004,
  reasoningUsd: 0,
  totalUsd: 0.000425,
};

describe("buildLedger", () => {
  it("renders input and output rows for a plain run", () => {
    const { categories, totalUsd } = buildLedger(baseUsage, baseCosts);
    expect(categories.map((c) => c.key)).toEqual(["input", "output"]);
    expect(categories[0].tokens).toBe(100);
    expect(categories[0].usd).toBeCloseTo(0.000025);
    expect(totalUsd).toBeCloseTo(0.000425);
  });

  it("renders reasoning row only when reasoning tokens are non-zero", () => {
    const withZero = buildLedger(
      { ...baseUsage, reasoningTokens: 0 },
      { ...baseCosts, reasoningUsd: 0 },
    );
    expect(withZero.categories.map((c) => c.key)).toEqual(["input", "output"]);

    const withReasoning = buildLedger(
      { ...baseUsage, reasoningTokens: 50 },
      { ...baseCosts, reasoningUsd: 0.00075 },
    );
    const reasoning = withReasoning.categories.find((c) => c.key === "reasoning");
    expect(reasoning).toBeDefined();
    expect(reasoning?.tokens).toBe(50);
    expect(reasoning?.usd).toBeCloseTo(0.00075);
  });

  it("renders tools row only when tool calls exist", () => {
    const noTools = buildLedger(baseUsage, baseCosts);
    expect(noTools.categories.map((c) => c.key)).not.toContain("tools");

    const withTools = buildLedger(
      { ...baseUsage, toolTokens: 80, toolCalls: 2 },
      baseCosts,
    );
    const tools = withTools.categories.find((c) => c.key === "tools");
    expect(tools).toBeDefined();
    expect(tools?.calls).toBe(2);
    expect(tools?.tokens).toBe(80);
  });

  it("renders all four categories when everything is non-zero", () => {
    const { categories } = buildLedger(
      { ...baseUsage, reasoningTokens: 50, toolTokens: 80, toolCalls: 2 },
      { ...baseCosts, reasoningUsd: 0.00075 },
    );
    expect(categories.map((c) => c.key)).toEqual([
      "input",
      "output",
      "reasoning",
      "tools",
    ]);
  });

  it("gives each category a distinct color variable", () => {
    const { categories } = buildLedger(
      { ...baseUsage, reasoningTokens: 50, toolTokens: 80, toolCalls: 2 },
      { ...baseCosts, reasoningUsd: 0.00075 },
    );
    const colorVars = categories.map((c) => c.colorVar);
    expect(new Set(colorVars).size).toBe(colorVars.length);
    expect(colorVars.every((v) => v.startsWith("--ledger-"))).toBe(true);
  });
});
