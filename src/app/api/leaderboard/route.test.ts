import { describe, it, expect, afterAll } from "vitest";
import { eq, inArray } from "drizzle-orm";
import { GET } from "./route";
import { USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users, scores } from "@/db/schema";

const U1 = "lb-route-u1";
const U2 = "lb-route-u2";
const SEED_IDS = [U1, U2];

function cookieFor(id: string): string {
  return `${USER_COOKIE}=${id}`;
}

function seedUser(id: string, username: string): void {
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

function resetProgress(): void {
  const db = getDb();
  db.delete(scores).where(inArray(scores.userId, SEED_IDS)).run();
}

afterAll(() => {
  const db = getDb();
  db.delete(scores).where(inArray(scores.userId, SEED_IDS)).run();
  db.delete(users).where(inArray(users.id, SEED_IDS)).run();
});

describe("GET /api/leaderboard (thru + best-per-hole)", () => {
  it("counts Thru as distinct recorded challenges; retries count once at their best", async () => {
    resetProgress();
    seedUser(U1, "Thru-Test-Tiger");
    seedUser(U2, "Thru-Test-Rory");
    // u1: two retries on hole 1 (only lowest counts) + one score on hole 2
    seedScore(U1, 1, 0.010);
    seedScore(U1, 1, 0.002);
    seedScore(U1, 2, 0.004);
    // u2: one recorded hole
    seedScore(U2, 1, 0.003);

    const res = await GET(new Request("http://localhost:3000/api/leaderboard"));
    expect(res.status).toBe(200);
    const data = await res.json();

    const mine = data.leaderboard.find(
      (r: { userId: string }) => r.userId === U1,
    );
    expect(mine).toBeDefined();
    // thru: two distinct recorded holes (retries on hole 1 count once)
    expect(mine.holes).toBe(2);
    // total: lowest per hole summed — min(0.010, 0.002) + 0.004 = 0.006
    expect(mine.totalUsd).toBeCloseTo(0.006, 6);

    const other = data.leaderboard.find(
      (r: { userId: string }) => r.userId === U2,
    );
    expect(other.holes).toBe(1);
    expect(other.totalUsd).toBeCloseTo(0.003, 6);
    // relative ranking: u2's 0.003 beats u1's 0.006 (other workers share the
    // temp DB, so absolute ranks are not stable — compare within the seed set)
    expect(other.rank).toBeLessThan(mine.rank);
  });

  it("exposes currentUserId from the cookie and omits users without scores", async () => {
    resetProgress();
    seedUser(U1, "Thru-Test-Cookie");
    const res = await GET(
      new Request("http://localhost:3000/api/leaderboard", {
        headers: { cookie: cookieFor(U1) },
      }),
    );
    const data = await res.json();
    expect(data.currentUserId).toBe(U1);
    // a user with no recorded scores has no leaderboard row
    expect(
      data.leaderboard.find((r: { userId: string }) => r.userId === U1),
    ).toBeUndefined();
  });
});
