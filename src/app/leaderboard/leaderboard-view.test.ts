import { describe, it, expect } from "vitest";
import { collapseRows, ordinal, type LeaderboardEntry } from "./leaderboard-view";

function entry(rank: number, userId = `u${rank}`): LeaderboardEntry {
  return {
    userId,
    username: `Player-${rank}`,
    totalUsd: rank * 0.001,
    holes: 1,
    rank,
  };
}

describe("collapseRows", () => {
  it("returns all rows when count fits within top ten plus one", () => {
    const entries = Array.from({ length: 11 }, (_, i) => entry(i + 1));
    expect(collapseRows(entries, null)).toEqual(entries);
  });

  it("collapses middle rows when user is in the top ten", () => {
    const entries = Array.from({ length: 20 }, (_, i) => entry(i + 1));
    const rows = collapseRows(entries, "u1");
    expect(rows[0]).toEqual(entries[0]);
    expect(rows[10]).toBe("collapsed");
    expect(rows[11]).toEqual(entries[19]);
  });

  it("shows the current user's row below the collapse when outside the top ten", () => {
    const entries = Array.from({ length: 20 }, (_, i) => entry(i + 1));
    const rows = collapseRows(entries, "u15");
    expect(rows.slice(0, 10)).toEqual(entries.slice(0, 10));
    expect(rows[10]).toBe("collapsed");
    expect(rows[11]).toEqual(entries[14]);
    expect(rows[12]).toBe("collapsed");
    expect(rows[13]).toEqual(entries[19]);
  });

  it("shows collapse-then-last when the current user is last", () => {
    const entries = Array.from({ length: 20 }, (_, i) => entry(i + 1));
    const rows = collapseRows(entries, "u20");
    expect(rows[10]).toBe("collapsed");
    expect(rows[11]).toEqual(entries[19]);
  });
});

describe("ordinal", () => {
  it("formats golf placements", () => {
    expect(ordinal(1)).toBe("1st");
    expect(ordinal(2)).toBe("2nd");
    expect(ordinal(3)).toBe("3rd");
    expect(ordinal(4)).toBe("4th");
    expect(ordinal(11)).toBe("11th");
    expect(ordinal(21)).toBe("21st");
    expect(ordinal(115)).toBe("115th");
  });
});
