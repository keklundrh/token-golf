import { sql, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { users, scores } from "@/db/schema";
import { readCookie, USER_COOKIE } from "@/lib/cookies";

export interface LeaderboardRow {
  userId: string;
  username: string;
  totalUsd: number;
  holes: number;
  rank: number;
}

export async function GET(request: Request): Promise<Response> {
  const db = getDb();
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

  const leaderboard: LeaderboardRow[] = rows.map((r, i) => ({
    ...r,
    totalUsd: Number(r.totalUsd),
    holes: Number(r.holes),
    rank: i + 1,
  }));

  const cookieUserId = readCookie(request.headers.get("cookie"), USER_COOKIE);
  return Response.json({ leaderboard, currentUserId: cookieUserId });
}

