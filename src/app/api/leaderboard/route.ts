import { getDb } from "@/db";
import { readCookie, USER_COOKIE } from "@/lib/cookies";
import { fetchLeaderboardRows, type LeaderboardEntryRow } from "@/db/leaderboard";

export async function GET(request: Request): Promise<Response> {
  const leaderboard: LeaderboardEntryRow[] = await fetchLeaderboardRows(getDb());
  const cookieUserId = readCookie(request.headers.get("cookie"), USER_COOKIE);
  return Response.json({ leaderboard, currentUserId: cookieUserId });
}

