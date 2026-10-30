import { formatMicroUsd } from "@/lib/currency";

export interface LeaderboardEntry {
  userId: string;
  username: string;
  totalUsd: number;
  holes: number;
  rank: number;
}

export function collapseRows(
  entries: LeaderboardEntry[],
  currentUserId: string | null,
): Array<LeaderboardEntry | "collapsed"> {
  const TOP_N = 10;
  if (entries.length <= TOP_N + 1) return entries;

  const mine = entries.find((e) => e.userId === currentUserId);
  if (!mine || mine.rank <= TOP_N) {
    return [...entries.slice(0, TOP_N), "collapsed", entries[entries.length - 1]];
  }
  if (mine.rank === entries[entries.length - 1].rank) {
    // the current user is the final player: one separator, their row last
    return [...entries.slice(0, TOP_N), "collapsed", mine];
  }
  return [
    ...entries.slice(0, TOP_N),
    "collapsed",
    mine,
    "collapsed" as const,
    entries[entries.length - 1],
  ];
}

export function ordinal(n: number): string {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] ?? s[v] ?? s[0]);
}

export default function LeaderboardView({
  leaderboard,
  currentUserId,
}: {
  leaderboard: LeaderboardEntry[];
  currentUserId: string | null;
}) {
  const rows = collapseRows(leaderboard, currentUserId);
  const mine = leaderboard.find((e) => e.userId === currentUserId);

  return (
    <main className="flex min-h-screen flex-col bg-white px-6 py-8 text-black">
      <div className="mx-auto flex w-full max-w-xl flex-col gap-6">
        <h1 className="text-center text-3xl font-semibold tracking-tight">Leaderboard</h1>
        {mine && (
          <p className="text-center text-lg">
            You are <span className="font-bold">{ordinal(mine.rank)}</span> of{" "}
            {leaderboard.length} — total spend{" "}
            <span className="font-bold">{formatMicroUsd(mine.totalUsd)}</span>
          </p>
        )}
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-left text-zinc-500">
              <th className="py-2 pr-2">Pos</th>
              <th className="py-2 pr-2">Player</th>
              <th className="py-2 pr-2 text-right">Thru</th>
              <th className="py-2 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) =>
              row === "collapsed" ? (
                <tr key={`collapsed-${i}`} className="text-center text-zinc-400">
                  <td colSpan={4} className="py-1">
                    ···
                  </td>
                </tr>
              ) : (
                <tr
                  key={row.userId}
                  className={`border-b border-zinc-100 ${
                    row.userId === currentUserId ? "font-bold" : ""
                  }`}
                >
                  <td className="py-2 pr-2">{row.rank}</td>
                  <td className="py-2 pr-2">{row.username}</td>
                  <td className="py-2 pr-2 text-right text-zinc-500">{row.holes}</td>
                  <td className="py-2 text-right">{formatMicroUsd(row.totalUsd)}</td>
                </tr>
              ),
            )}
          </tbody>
        </table>
        <a
          href="/"
          className="flex h-12 items-center justify-center rounded-full border border-zinc-300 text-center font-medium hover:bg-zinc-50"
        >
          Play Again
        </a>
      </div>
    </main>
  );
}
