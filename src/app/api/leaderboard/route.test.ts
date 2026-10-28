import { describe, it, expect } from "vitest";
import { GET } from "./route";
import { USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users, scores } from "@/db/schema";

const USER_ID = "lb-test-user";
const OTHER_ID = "lb-other-user";

function cookie(): string {
  return `${USER_COOKIE}=${USER_ID}`;
}

function ensureUser(id: string, username: string): void {
  getDb()
    .insert(users)
    .values({ id, username, createdAt: Date.now() })
    .onConflictDoNothing()
    .run();
}

function seedScore(userId: string, challengeId: number, costUsd: number): void {
  getDb()
    .insert(scores)
    .values({ userId, challengeId, costUsd, recordedAt: Date.now() })
    .run();
}

describe("GET /api/leaderboard best-per-hole aggregation", () => {
  it("sums the lowest recorded score per hole, not all attempts", async () => {
    ensureUser(USER_ID, "lb-test");
    ensureUser(OTHER_ID, "lb-other");
    // same hole recorded twice for USER_ID: 5000 µ$ then 2000 µ$ -> only 2000 counts
    seedScore(USER_ID, 1, 0.005);
    seedScore(USER_ID, 1, 0.002);
    seedScore(USER_ID, 2, 0.001);
    seedScore(OTHER_ID, 1, 0.004);

    const res = await GET(new Request("http://localhost:3000/api/leaderboard"));
    expect(res.ok).toBe(true);
    const data = await res.json();
    const mine = data.leaderboard.find((e: { userId: string }) => e.userId === USER_ID);
    // 0.002 (best hole 1) + 0.001 (hole 2) = 0.003 USD, holes = 2
    expect(mine.totalUsd).toBeCloseTo(0.003, 6);
    expect(mine.holes).toBe(2);
    const other = data.leaderboard.find((e: { userId: string }) => e.userId === OTHER_ID);
    expect(other.totalUsd).toBeCloseTo(0.004, 6);
  });
});
