import { describe, it, expect, afterAll } from "vitest";
import { eq } from "drizzle-orm";
import { POST } from "./route";
import { USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users, attempts, scores } from "@/db/schema";

const USER_ID = "reset-test-user";

function cookie(): string {
  return `${USER_COOKIE}=${USER_ID}`;
}

ensureUser();

function ensureUser(): void {
  getDb()
    .insert(users)
    .values({ id: USER_ID, username: "reset-test", createdAt: Date.now() })
    .onConflictDoNothing()
    .run();
}

function seedProgress(): void {
  const db = getDb();
  db.insert(attempts)
    .values({ userId: USER_ID, challengeId: 1, optionId: "a", costUsd: 0.002, createdAt: Date.now() })
    .run();
  db.insert(scores)
    .values({ userId: USER_ID, challengeId: 1, costUsd: 0.002, recordedAt: Date.now() })
    .run();
}

afterAll(() => {
  const db = getDb();
  db.delete(attempts).where(eq(attempts.userId, USER_ID)).run();
  db.delete(scores).where(eq(scores.userId, USER_ID)).run();
});

describe("POST /api/game/reset (Start Playing = abandoned game starts over)", () => {
  it("clears attempts AND recorded scores; the identity survives", async () => {
    ensureUser();
    seedProgress();

    const res = await POST(
      new Request("http://localhost:3000/api/game/reset", {
        method: "POST",
        headers: { cookie: cookie() },
      }),
    );
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.ok).toBe(true);

    const db = getDb();
    // attempts cleared (fresh swings, cap counter reset)
    expect(db.select().from(attempts).where(eq(attempts.userId, USER_ID)).all()).toHaveLength(0);
    // recorded scores cleared (an abandoned game does not carry spend into the next round)
    expect(db.select().from(scores).where(eq(scores.userId, USER_ID)).all()).toHaveLength(0);
    // the user identity itself survives
    expect(db.select().from(users).where(eq(users.id, USER_ID)).all()).toHaveLength(1);
  });

  it("returns 401 without a user cookie", async () => {
    const res = await POST(
      new Request("http://localhost:3000/api/game/reset", { method: "POST" }),
    );
    expect(res.status).toBe(401);
  });
});
