import { sql, eq } from "drizzle-orm";
import type { Db } from "@/db";
import { users, scores } from "@/db/schema";

export interface LeaderboardEntryRow {
  userId: string;
  username: string;
  totalUsd: number;
  holes: number;
  rank: number;
}

/**
 * The one leaderboard aggregation: total = sum over holes of the player's
 * LOWEST recorded score per hole (golf: best round on a hole is your score);
 * Thru = distinct recorded challenges. Only players with >= 1 recorded
 * score appear (inner join). Owned by #6 — both the API route and the SSR
 * page call this, so the Spend header and board totals can never diverge.
 */
export async function fetchLeaderboardRows(db: Db): Promise<LeaderboardEntryRow[]> {
  const rows = await db
    .select({
      userId: users.id,
      username: users.username,
      // golf: sum of the lowest recorded score per hole — retries only count once, at their best
      totalUsd: sql<number>`CAST((SELECT SUM(best) FROM (SELECT MIN(s2.cost_usd) AS best FROM scores s2 WHERE s2.user_id = ${users.id} GROUP BY s2.challenge_id)) AS REAL)`,
      holes: sql<number>`COUNT(DISTINCT ${scores.challengeId})`,
    })
    .from(users)
    .innerJoin(scores, eq(users.id, scores.userId))
    .groupBy(users.id, users.username)
    .orderBy(sql`(SELECT SUM(best) FROM (SELECT MIN(s2.cost_usd) AS best FROM scores s2 WHERE s2.user_id = ${users.id} GROUP BY s2.challenge_id)) ASC`);

  return rows.map((r, i) => ({
    ...r,
    totalUsd: Number(r.totalUsd),
    holes: Number(r.holes),
    rank: i + 1,
  }));
}
