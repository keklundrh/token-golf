import { describe, it, expect } from "vitest";
import { buildLedger, buildRunBlocks, cacheRowLabel, relativeTime, type RunRecord } from "./ledger";
import type { TokenUsage } from "./cost";

const baseUsage: TokenUsage & {
  toolTokens: number;
  toolCalls: number;
  cacheReadTokens: number | null;
  cacheWriteTokens: number | null;
} = {
  inputTokens: 100,
  outputTokens: 200,
  reasoningTokens: null,
  cacheReadTokens: null,
  cacheWriteTokens: null,
  toolTokens: 0,
  toolCalls: 0,
};

function makeRun(overrides: Partial<RunRecord> & { optionId: string; optionLabel: string; timestamp: number }): RunRecord {
  return {
    usage: { ...baseUsage, inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0 },
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
        usage: { ...baseUsage, reasoningTokens: 50, toolTokens: 80, toolCalls: 2, inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0.00075, cacheReadUsd: 0, cacheWriteUsd: 0 },
        costUsd: 0.00118,
        flags: { thinking: true, tools: true },
      }),
      makeRun({ optionId: "plain", optionLabel: "Plain run", timestamp: now - 60_000 }),
    ];
    const blocks = buildRunBlocks(runs, now);
    expect(blocks[0].ledger.categories.map((c) => c.key)).toEqual(["input", "output", "reasoning", "tools"]);
    expect(blocks[0].ledger.totalUsd).toBeCloseTo(0.00118);
    expect(blocks[1].ledger.categories.map((c) => c.key)).toEqual(["input", "output"]);
    expect(blocks[1].ledger.totalUsd).toBeCloseTo(0.00043);
  });

  it("renders thinking/cache rows only when the option's flag is set", () => {
    // Training-display rule: an endpoint that reasons by default must not
    // show a thinking row the challenge didn't author.
    const runs = [
      makeRun({
        optionId: "reasons-by-default",
        optionLabel: "Local model",
        timestamp: now,
        usage: { ...baseUsage, reasoningTokens: 71, inputUsd: 0.000325, outputUsd: 0.002475, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0 },
        costUsd: 0.0028,
        // no flags: reasoning reported but not requested
      }),
      makeRun({
        optionId: "thinks",
        optionLabel: "With thinking",
        timestamp: now,
        usage: { ...baseUsage, reasoningTokens: 71, inputUsd: 0.000325, outputUsd: 0.002475, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0 },
        costUsd: 0.0028,
        flags: { thinking: true },
      }),
    ];
    const blocks = buildRunBlocks(runs, now);
    expect(blocks[0].ledger.categories.map((c) => c.key)).toEqual(["input", "output"]);
    expect(blocks[1].ledger.categories.map((c) => c.key)).toEqual(["input", "output", "reasoning"]);
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
    const ledger = buildLedger(usage, { inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0, totalUsd: 0.00043 }, { tools: true });
    expect(ledger.categories.find((c) => c.key === "tools")?.calls).toBe(1);
    expect(ledger.totalUsd).toBeCloseTo(0.00043);
  });

  it("renders cache read/write rows only when non-zero and caching flag set", () => {
    // baseUsage inputTokens=100: 30 uncached + 50 read + 20 write
    const withCache = buildLedger(
      { ...baseUsage, cacheReadTokens: 50, cacheWriteTokens: 20 },
      { inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0, cacheReadUsd: 0.000015, cacheWriteUsd: 0.000075, totalUsd: 0.00052 },
      { caching: true },
    );
    expect(withCache.categories.map((c) => c.key)).toEqual(["input", "output", "cache-read", "cache-write"]);
    const cacheRead = withCache.categories.find((c) => c.key === "cache-read");
    expect(cacheRead?.tokens).toBe(50);
    expect(cacheRead?.colorVar).toBe("--ledger-cache-read");
    // no pricing passed: labels fall back to plain input charges
    expect(cacheRead?.label).toBe("input (cache hit)");
    const cacheWrite = withCache.categories.find((c) => c.key === "cache-write");
    expect(cacheWrite?.label).toBe("input (cache save)");
    expect(cacheWrite?.colorVar).toBe("--ledger-cache-write");
    // the input row shows only the tokens charged at input rate — the
    // cached tokens are listed in their own rows, so tok and µ$ agree
    expect(withCache.categories.find((c) => c.key === "input")?.tokens).toBe(30);

    const zeroCache = buildLedger(
      { ...baseUsage, cacheReadTokens: 0, cacheWriteTokens: null },
      { inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0, cacheReadUsd: 0, cacheWriteUsd: 0, totalUsd: 0.00043 },
      { caching: true },
    );
    expect(zeroCache.categories.map((c) => c.key)).toEqual(["input", "output"]);

    // non-zero cache tokens without the flag: no cache rows (training-
    // display rule), but the input-row math mirrors computeCost
    // unconditionally — tokens charged at input rate only, so tok and µ$
    // agree even with the cache rows hidden
    const unflagged = buildLedger(
      { ...baseUsage, cacheReadTokens: 50, cacheWriteTokens: 20 },
      { inputUsd: 0.00003, outputUsd: 0.0004, reasoningUsd: 0, cacheReadUsd: 0.000015, cacheWriteUsd: 0.000075, totalUsd: 0.00052 },
    );
    expect(unflagged.categories.map((c) => c.key)).toEqual(["input", "output"]);
    expect(unflagged.categories.find((c) => c.key === "input")?.tokens).toBe(30);
  });
  it("derives cache row labels from the model's pricing", () => {
    const price = { input_per_mtok: 3.0, cache_read_per_mtok: 0.3, cache_write_per_mtok: 3.75 };
    expect(cacheRowLabel(price, "read")).toBe("input × 0.1 (cache hit)");
    expect(cacheRowLabel(price, "write")).toBe("input × 1.25 (cache save)");
  });

  it("falls back to plain input labels when cache pricing is null", () => {
    const price = { input_per_mtok: 1.0, cache_read_per_mtok: null, cache_write_per_mtok: null };
    expect(cacheRowLabel(price, "read")).toBe("input (cache hit)");
    expect(cacheRowLabel(price, "write")).toBe("input (cache save)");
    expect(cacheRowLabel(undefined, "read")).toBe("input (cache hit)");
  });
});
