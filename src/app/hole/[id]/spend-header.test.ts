import { describe, it, expect } from "vitest";
import { spendFromLeaderboard, formatSpendHeader } from "./spend-header";

const data = {
  leaderboard: [
    { userId: "u1", totalUsd: 0.001 },
    { userId: "me", totalUsd: 0.002 },
  ],
  currentUserId: "me",
};

describe("spendFromLeaderboard", () => {
  it("returns the current user's recorded total", () => {
    expect(spendFromLeaderboard(data)).toBe(0.002);
  });

  it("returns 0 for a scoreless player", () => {
    expect(spendFromLeaderboard({ ...data, currentUserId: "nobody" })).toBe(0);
  });

  it("returns unknown on a failed fetch", () => {
    expect(spendFromLeaderboard(null)).toBe("unknown");
  });
});

describe("formatSpendHeader", () => {
  it("renders loading while the fetch is in flight", () => {
    expect(formatSpendHeader("loading", true)).toBe("Spend …");
  });

  it("renders a dash for an unknown total — never a false 0", () => {
    expect(formatSpendHeader("unknown", false)).toBe("Spend —");
  });

  it("renders the recorded total in micro-dollars", () => {
    expect(formatSpendHeader(0.002, false)).toBe("Spend 2,000 µ$");
  });

  it("renders 0 for a scoreless player", () => {
    expect(formatSpendHeader(0, false)).toBe("Spend 0 µ$");
  });
});
