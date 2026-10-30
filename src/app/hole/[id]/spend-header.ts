/**
 * Spend-header mapping per #5/#2 step 13: the header shows the player's
 * total of recorded scores, fetched once per hole mount and static while
 * on that hole. Loading renders "Spend …"; a failed fetch leaves the
 * total unknown ("Spend —") rather than a false 0.
 */

export interface LeaderboardSpendData {
  leaderboard: Array<{ userId: string; totalUsd: number }>;
  currentUserId: string | null;
}

export type SpendDisplay = "loading" | "unknown" | number;

/** Map the /api/leaderboard response to the header's spend state. */
export function spendFromLeaderboard(
  data: LeaderboardSpendData | null,
): SpendDisplay {
  if (!data) return "unknown";
  const mine = data.leaderboard.find((e) => e.userId === data.currentUserId);
  return mine ? mine.totalUsd : 0;
}

/** Render the header text from a spend state. */
export function formatSpendHeader(spend: SpendDisplay, loading: boolean): string {
  if (loading) return "Spend …";
  if (spend === "loading" || spend === "unknown") return "Spend —";
  return `Spend ${new Intl.NumberFormat("en-US").format(Math.round(spend * 1_000_000))} µ$`;
}
