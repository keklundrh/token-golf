import { describe, it, expect } from "vitest";
import { listChallengeIds, loadChallenge } from "./config";

describe("challenge discovery for auto-advance", () => {
  it("lists holes in order for next-hole routing", () => {
    const ids = listChallengeIds();
    expect(ids.length).toBeGreaterThan(0);
    expect([...ids].sort((a, b) => a - b)).toEqual(ids);
  });

  it("loads every discovered hole", () => {
    for (const id of listChallengeIds()) {
      const ch = loadChallenge(id);
      expect(ch.id).toBe(id);
    }
  });
});
