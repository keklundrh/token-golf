"use client";

import { useEffect, useState } from "react";

export interface LeaderboardEntry {
  userId: string;
  username: string;
  totalUsd: number;
  holes: number;
  rank: number;
}

interface LeaderboardData {
  leaderboard: LeaderboardEntry[];
  currentUserId: string | null;
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
  return [
    ...entries.slice(0, TOP_N),
    "collapsed",
    mine,
    "collapsed" as const,
    entries[entries.length - 1],
  ];
}

export default function Leaderboard() {
  const [data, setData] = useState<LeaderboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/leaderboard")
      .then(async (res) => {
        if (!res.ok) throw new Error(`leaderboard failed: ${res.status}`);
        setData(await res.json());
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white px-6">
        <p className="text-red-700">{error}</p>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white px-6">
        <p className="text-zinc-500">Loading leaderboard…</p>
      </main>
    );
  }

  const rows = collapseRows(data.leaderboard, data.currentUserId);
  const mine = data.leaderboard.find((e) => e.userId === data.currentUserId);

  return (
    <main className="flex min-h-screen flex-col bg-white px-6 py-8 text-black">
      <div className="mx-auto flex w-full max-w-xl flex-col gap-6">
        <h1 className="text-center text-3xl font-semibold tracking-tight">Leaderboard</h1>
        {mine && (
          <p className="text-center text-lg">
            You are <span className="font-bold">{ordinal(mine.rank)}</span> of{" "}
            {data.leaderboard.length} — total spend{" "}
            <span className="font-bold">${mine.totalUsd.toFixed(4)}</span>
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
                    row.userId === data.currentUserId ? "font-bold" : ""
                  }`}
                >
                  <td className="py-2 pr-2">{row.rank}</td>
                  <td className="py-2 pr-2">{row.username}</td>
                  <td className="py-2 pr-2 text-right text-zinc-500">{row.holes}</td>
                  <td className="py-2 text-right">${row.totalUsd.toFixed(4)}</td>
                </tr>
              ),
            )}
          </tbody>
        </table>
        <button
          type="button"
          onClick={() => (window.location.href = "/")}
          className="h-12 rounded-full border border-zinc-300 font-medium hover:bg-zinc-50"
        >
          Play Again
        </button>
      </div>
    </main>
  );
}

export function ordinal(n: number): string {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] ?? s[v] ?? s[0]);
}
