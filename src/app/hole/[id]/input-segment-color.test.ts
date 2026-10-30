import { describe, it, expect } from "vitest";
import { inputSegmentColor } from "./challenge-view";

describe("inputSegmentColor", () => {
  it("is teal (cache-read) when the run read from cache", () => {
    expect(inputSegmentColor({ cacheReadTokens: 1_154, cacheWriteTokens: 0 })).toBe(
      "var(--ledger-cache-read)",
    );
  });

  it("is darker teal (cache-write) when the run wrote the cache", () => {
    expect(inputSegmentColor({ cacheReadTokens: 0, cacheWriteTokens: 1_154 })).toBe(
      "var(--ledger-cache-write)",
    );
  });

  it("prefers cache-read when both are reported", () => {
    expect(inputSegmentColor({ cacheReadTokens: 10, cacheWriteTokens: 5 })).toBe(
      "var(--ledger-cache-read)",
    );
  });

  it("is blue (input rate) when no cache tokens are reported", () => {
    expect(inputSegmentColor({ cacheReadTokens: 0, cacheWriteTokens: 0 })).toBe(
      "var(--ledger-input)",
    );
    expect(inputSegmentColor(null)).toBe("var(--ledger-input)");
  });
});
