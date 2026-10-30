
import { headers } from "next/headers";
import { unstable_noStore } from "next/cache";
import { getDb } from "@/db";
import { readCookie, USER_COOKIE } from "@/lib/cookies";
import { fetchLeaderboardRows } from "@/db/leaderboard";
import LeaderboardView, { type LeaderboardEntry } from "./leaderboard-view";

// Next 16 blocking-prerender guard: this route reads runtime data
// (unstable_noStore + cookies), so the build must not prerender it.
export const instant = false;

export default async function LeaderboardPage() {
  unstable_noStore(); // runtime data: the leaderboard is per-request, never prerendered
  const cookieHeader = (await headers()).get("cookie");
  const rows = await fetchLeaderboardRows(getDb());
  const leaderboard: LeaderboardEntry[] = rows;
  return (
    <LeaderboardView
      leaderboard={leaderboard}
      currentUserId={readCookie(cookieHeader, USER_COOKIE)}
    />
  );
}
