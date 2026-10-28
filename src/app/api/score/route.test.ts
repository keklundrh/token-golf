import { describe, it, expect, afterAll } from "vitest";
import { and, eq } from "drizzle-orm";
import { POST } from "./route";
import { USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users, scores, attempts } from "@/db/schema";

const USER_ID = "score-test-user";
const OTHER_ID = "score-other-user";

function body(challengeId: number, optionId: string, cookie?: string): Request {
  return new Request("http://localhost:3000/api/score", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(cookie ? { cookie } : {}) },
    body: JSON.stringify({ challengeId, optionId }),
  });
}

function cookieFor(id: string): string {
  return `${USER_COOKIE}=${id}`;
}

function ensureUser(id: string, username: string): void {
  getDb()
    .insert(users)
    .values({ id, username, createdAt: Date.now() })
    .onConflictDoNothing()
    .run();
}

function seedAttempt(userId: string, challengeId: number, optionId: string, costUsd: number): void {
  getDb()
    .insert(attempts)
    .values({ userId, challengeId, optionId, costUsd, createdAt: Date.now() })
    .run();
}

/** Per-test isolation: only rows for this exact (user, challenge, option) matter. */
function resetProgress(challengeId?: number): void {
  const db = getDb();
  db.delete(scores).where(
    challengeId === undefined
      ? eq(scores.userId, USER_ID)
      : and(eq(scores.userId, USER_ID), eq(scores.challengeId, challengeId)),
  ).run();
  db.delete(attempts).where(
    challengeId === undefined
      ? eq(attempts.userId, USER_ID)
      : and(eq(attempts.userId, USER_ID), eq(attempts.challengeId, challengeId)),
  ).run();
}

function scoreFor(challengeId: number): { costUsd: number } | undefined {
  return getDb()
    .select({ costUsd: scores.costUsd })
    .from(scores)
    .where(and(eq(scores.userId, USER_ID), eq(scores.challengeId, challengeId)))
    .get();
}

afterAll(() => {
  const db = getDb();
  db.delete(attempts).where(eq(attempts.userId, USER_ID)).run();
  db.delete(scores).where(eq(scores.userId, USER_ID)).run();
  db.delete(attempts).where(eq(attempts.userId, OTHER_ID)).run();
  db.delete(scores).where(eq(scores.userId, OTHER_ID)).run();
});

describe("POST /api/score (server-measured scoring)", () => {
  it("records the server-measured attempt cost, ignoring any client-supplied costUsd", async () => {
    ensureUser(USER_ID, "score-test");
    resetProgress(1);
    seedAttempt(USER_ID, 1, "large-input", 0.003792);

    // attacker payload: client claims a zero-cost run (extra body keys are ignored;
    // the cookie identifies the user, the server-measured attempt is the cost)
    const res = await POST(
      new Request("http://localhost:3000/api/score", {
        method: "POST",
        headers: { "Content-Type": "application/json", cookie: cookieFor(USER_ID) },
        body: JSON.stringify({ challengeId: 1, optionId: "large-input", costUsd: 0 }),
      }),
    );
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.ok).toBe(true);

    // the stored cost is the server-measured attempt cost, not the client's 0
    expect(scoreFor(1)?.costUsd).toBeCloseTo(0.003792, 6);
  });

  it("keeps the lowest score when the same hole is recorded twice", async () => {
    ensureUser(USER_ID, "score-test");
    resetProgress(1);
    seedAttempt(USER_ID, 1, "large-input", 0.001); // better retry attempt

    const res = await POST(body(1, "large-input", cookieFor(USER_ID)));
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.kept).toBeUndefined(); // updated to the lower score

    expect(scoreFor(1)?.costUsd).toBeCloseTo(0.001, 6);
  });

  it("keeps the existing (lowest) score when a retry attempt is worse", async () => {
    ensureUser(USER_ID, "score-test");
    // self-contained: seed the earlier lowest score this test keeps
    resetProgress(1);
    seedAttempt(USER_ID, 1, "large-input", 0.001);
    const first = await POST(body(1, "large-input", cookieFor(USER_ID)));
    expect(first.status).toBe(200);
    seedAttempt(USER_ID, 1, "large-input", 0.02); // worse attempt

    const res = await POST(body(1, "large-input", cookieFor(USER_ID)));
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.kept).toBe("existing (lowest)");

    // still the earlier lowest score
    expect(scoreFor(1)?.costUsd).toBeCloseTo(0.001, 6);
  });

  it("returns 409 when no practice swing was taken for the option", async () => {
    ensureUser(OTHER_ID, "score-other");
    const res = await POST(body(1, "large-input", cookieFor(OTHER_ID)));
    expect(res.status).toBe(409);
    const data = await res.json();
    expect(data.error).toBe("no practice swing taken for this option");
  });

  it("returns 409 when the recorded option was never run (only another option was)", async () => {
    ensureUser(USER_ID, "score-test");
    resetProgress(2);
    seedAttempt(USER_ID, 2, "large-input", 0.003792);
    const res = await POST(body(2, "terse", cookieFor(USER_ID)));
    expect(res.status).toBe(409);
    const data = await res.json();
    expect(data.error).toBe("no practice swing taken for this option");
  });

  it("records the chosen option's attempt when multiple options ran", async () => {
    ensureUser(USER_ID, "score-test");
    resetProgress(2);
    // option A ran cheap, option B ran expensive; user records A's run
    seedAttempt(USER_ID, 2, "large-input", 0.001);
    seedAttempt(USER_ID, 2, "verbose", 0.02);
    const res = await POST(body(2, "large-input", cookieFor(USER_ID)));
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.ok).toBe(true);
    // the recorded cost is option A's server-measured attempt, not the latest run
    expect(scoreFor(2)?.costUsd).toBeCloseTo(0.001, 6);
  });

  it("re-recording a worse option keeps the existing (lowest) score", async () => {
    // self-contained: record the cheap A first, then the expensive B keeps lowest
    ensureUser(USER_ID, "score-test");
    resetProgress(2);
    seedAttempt(USER_ID, 2, "large-input", 0.001);
    seedAttempt(USER_ID, 2, "verbose", 0.02);
    await POST(body(2, "large-input", cookieFor(USER_ID)));
    const res = await POST(body(2, "verbose", cookieFor(USER_ID)));
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.kept).toBe("existing (lowest)");
    expect(scoreFor(2)?.costUsd).toBeCloseTo(0.001, 6);
  });

  it("returns 401 without a user cookie", async () => {
    const res = await POST(body(1, "large-input"));
    expect(res.status).toBe(401);
  });

  it("returns 404 for an unknown challenge", async () => {
    ensureUser(USER_ID, "score-test");
    const res = await POST(body(999, "large-input", cookieFor(USER_ID)));
    expect(res.status).toBe(404);
  });
});
