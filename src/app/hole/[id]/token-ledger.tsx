"use client";

import type { LedgerRowData } from "@/lib/ledger";

export default function TokenLedger({
  categories,
  totalUsd,
}: LedgerRowData) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-3">
      <div className="flex flex-col gap-1.5">
        {categories.map((cat) => (
          <div key={cat.key} className="flex items-center gap-2 text-xs">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ background: `var(${cat.colorVar})` }}
            />
            <span className="font-medium text-black">{cat.label}</span>
            {cat.calls !== undefined && (
              <span className="text-zinc-500">{cat.calls} call{cat.calls === 1 ? "" : "s"}</span>
            )}
            <span className="text-zinc-500">{cat.tokens.toLocaleString()} tok</span>
            <span className="ml-auto font-mono text-zinc-700">
              ${cat.usd.toFixed(cat.usd === 0 ? 2 : 6)}
            </span>
          </div>
        ))}
        <div className="mt-1 flex items-center justify-between border-t border-zinc-100 pt-1.5 text-xs">
          <span className="font-semibold text-black">total</span>
          <span className="font-mono font-semibold text-black">${totalUsd.toFixed(6)}</span>
        </div>
      </div>
    </div>
  );
}
