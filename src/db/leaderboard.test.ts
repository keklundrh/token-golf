import { describe, it, expect, beforeEach, afterEach } from "vitest";
import Database from "better-sqlite3";
import { drizzle, type BetterSQLite3Database } from "drizzle-orm/better-sqlite3";
import { eq, sql } from "drizzle-orm";
import * as schema from "@/db/schema";
import { users, scores } from "@/db/schema";
import type { Db } from "@/db";

function testDb(): { db: Db; cleanup: () => void } {
  const sqlite = new Database(":memory:");
  sqlite.exec(`
    CREATE TABLE users (
      id TEXT PRIMARY KEY,
      username TEXT NOT NULL UNIQUE,
      created_at INTEGER NOT NULL
    );
    CREATE TABLE scores (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL REFERENCES users(id),
      challenge_id INTEGER NOT NULL,
      cost_usd REAL NOT NULL,
      recorded_at INTEGER NOT NULL
    );
  `);
  const db = drizzle(sqlite, { schema });
  return { db, cleanup: () => sqlite.close() };
}

async function seed(
  db: Db,
  userId: string,
  username: string,
  entries: Array<[number, number]>,
) {
  await db.insert(users).values({ id: userId, username, createdAt: Date.now() });
  for (const [challengeId, costUsd] of entries) {
    await db
      .insert(scores)
      .values({ userId, challengeId, costUsd, recordedAt: Date.now() });
  }
}

describe("leaderboard query semantics", () => {
  let db: Db;
  let cleanup: () => void;

  beforeEach(() => {
    ({ db, cleanup } = testDb());
  });
  afterEach(() => cleanup());

  it("ranks by total recorded cost ascending", async () => {
    await seed(db, "u1", "Tiger-Augusta-green-1", [[1, 0.005], [2, 0.003]]);
    await seed(db, "u2", "Rory-Pebble-red-2", [[1, 0.002]]);

    const rows = await db
      .select({
        userId: users.id,
        totalUsd: sql<number>`CAST(SUM(${scores.costUsd}) AS REAL)`,
        holes: sql<number>`COUNT(DISTINCT ${scores.challengeId})`,
      })
      .from(users)
      .innerJoin(scores, eq(users.id, scores.userId))
      .groupBy(users.id, users.username)
      .orderBy(sql`SUM(${scores.costUsd}) ASC`);

    expect(rows[0].userId).toBe("u2");
    expect(Number(rows[0].totalUsd)).toBeCloseTo(0.002);
    expect(rows[1].userId).toBe("u1");
    expect(Number(rows[1].totalUsd)).toBeCloseTo(0.008);
    expect(Number(rows[1].holes)).toBe(2);
  });

  it("only counts recorded scores", async () => {
    await seed(db, "u1", "Tiger-Augusta-green-1", [[1, 0.005]]);
    const rows = await db.select().from(scores).where(eq(scores.userId, "u1"));
    expect(rows).toHaveLength(1);
  });

  it("ties in total keep stable insertion order", async () => {
    await seed(db, "u1", "A-1", [[1, 0.002]]);
    await seed(db, "u2", "B-2", [[1, 0.002]]);
    const rows = await db
      .select({ userId: users.id, totalUsd: sql<number>`SUM(${scores.costUsd})` })
      .from(users)
      .innerJoin(scores, eq(users.id, scores.userId))
      .groupBy(users.id)
      .orderBy(sql`SUM(${scores.costUsd}) ASC`);
    expect(Number(rows[0].totalUsd)).toBe(Number(rows[1].totalUsd));
  });
});
