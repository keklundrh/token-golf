import { describe, it, expect } from "vitest";
import { buildLedger, buildRunBlocks, relativeTime, type RunRecord } from "./ledger";
import type { TokenUsage } from "./cost";

const baseUsage: TokenUsage & { toolTokens: number; toolCalls: number } = {
  inputTokens: 100,
  outputTokens: 200,
  reasoningTokens: null,
  toolTokens: 0,
  toolCalls: 0,
};

function makeRun(overrides: Partial<RunRecord> & { optionId: string; optionLabel: string; timestamp: number }): RunRecord {
  return {
    usage: { ...baseUsage, inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0 },
    costUsd: 0.00043,
    recorded: false,
    ...overrides,
  };
}

describe("relativeTime", () => {
  const now = Date.parse("2026-01-01T12:00:00Z");

  it("returns just now for timestamps under a minute old", () => {
    expect(relativeTime(now - 30_000, now)).toBe("just now");
    expect(relativeTime(now, now)).toBe("just now");
  });

  it("returns Xm ago for timestamps under an hour old", () => {
    expect(relativeTime(now - 60_000, now)).toBe("1m ago");
    expect(relativeTime(now - 5 * 60_000, now)).toBe("5m ago");
    expect(relativeTime(now - 59 * 60_000, now)).toBe("59m ago");
  });

  it("returns Xh ago for timestamps an hour or older", () => {
    expect(relativeTime(now - 60 * 60_000, now)).toBe("1h ago");
    expect(relativeTime(now - 3 * 60 * 60_000, now)).toBe("3h ago");
  });
});

describe("buildRunBlocks", () => {
  const now = Date.parse("2026-01-01T12:00:00Z");

  it("renders runs oldest first: array order is chronological, newest last", () => {
    const runs = [
      makeRun({ optionId: "big-input", optionLabel: "Large input", timestamp: now - 5 * 60_000 }),
      makeRun({ optionId: "explain", optionLabel: "Detailed explanation", timestamp: now - 30_000 }),
    ];
    const blocks = buildRunBlocks(runs, now);
    expect(blocks.map((b) => b.optionLabel)).toEqual(["Large input", "Detailed explanation"]);
    expect(blocks[0].timeLabel).toBe("5m ago");
    expect(blocks[1].timeLabel).toBe("just now");
  });

  it("numbers runs 1-based in chronological array order (Run 1 = oldest, at the top)", () => {
    const runs = [
      makeRun({ optionId: "a", optionLabel: "A", timestamp: now - 120_000 }),
      makeRun({ optionId: "b", optionLabel: "B", timestamp: now - 60_000 }),
      makeRun({ optionId: "c", optionLabel: "C", timestamp: now }),
    ];
    const blocks = buildRunBlocks(runs, now);
    expect(blocks.map((b) => b.number)).toEqual([1, 2, 3]);
    expect(blocks[0].optionLabel).toBe("A");
    expect(blocks[2].optionLabel).toBe("C");
  });

  it("preserves per-run usage and cost", () => {
    const runs = [
      makeRun({
        optionId: "thinker",
        optionLabel: "Deep think",
        timestamp: now,
        usage: { ...baseUsage, reasoningTokens: 50, toolTokens: 80, toolCalls: 2, inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0.00075 },
        costUsd: 0.00118,
      }),
      makeRun({ optionId: "plain", optionLabel: "Plain run", timestamp: now - 60_000 }),
    ];
    const blocks = buildRunBlocks(runs, now);
    expect(blocks[0].ledger.categories.map((c) => c.key)).toEqual(["input", "output", "reasoning", "tools"]);
    expect(blocks[0].ledger.totalUsd).toBeCloseTo(0.00118);
    expect(blocks[1].ledger.categories.map((c) => c.key)).toEqual(["input", "output"]);
    expect(blocks[1].ledger.totalUsd).toBeCloseTo(0.00043);
  });

  it("carries recorded flags through to blocks", () => {
    const runs = [
      makeRun({ optionId: "a", optionLabel: "A", timestamp: now, recorded: true }),
      makeRun({ optionId: "b", optionLabel: "B", timestamp: now - 60_000 }),
    ];
    const blocks = buildRunBlocks(runs, now);
    expect(blocks.map((b) => b.recorded)).toEqual([true, false]);
  });

  it("handles an empty run history", () => {
    expect(buildRunBlocks([], Date.now())).toEqual([]);
  });
});

describe("run history model", () => {
  it("RunRecord stores usage and cost only — no segments field", () => {
    const run = makeRun({ optionId: "a", optionLabel: "A", timestamp: 0 });
    expect(Object.keys(run).sort()).toEqual([
      "costUsd",
      "optionId",
      "optionLabel",
      "recorded",
      "timestamp",
      "usage",
    ]);
  });

  it("per-run ledger builds independently via buildLedger", () => {
    const usage = { ...baseUsage, toolTokens: 40, toolCalls: 1 };
    const ledger = buildLedger(usage, { inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0, totalUsd: 0.00043 });
    expect(ledger.categories.find((c) => c.key === "tools")?.calls).toBe(1);
    expect(ledger.totalUsd).toBeCloseTo(0.00043);
  });
});
