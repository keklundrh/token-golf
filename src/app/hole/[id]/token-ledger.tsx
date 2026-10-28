import type { LedgerRowData, RunBlock } from "@/lib/ledger";
import { formatMicroUsd } from "@/lib/currency";

function LedgerBlock({
  ledger,
  header,
  indentHeader,
  recorded,
}: {
  ledger: LedgerRowData;
  header?: string;
  indentHeader?: boolean;
  recorded?: boolean;
}) {
  return (
    <div>
      {header && (
        <div className={`flex items-center text-xs ${indentHeader ? "pl-4" : ""}`}>
          <span className="font-medium text-black">{header}</span>
          {recorded && <span className="ml-auto text-zinc-500">recorded ✓</span>}
        </div>
      )}
      <div className={header ? "pl-4" : ""}>
        <div className="flex flex-col gap-1.5">
          {ledger.categories.map((cat) => (
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
                {formatMicroUsd(cat.usd)}
              </span>
            </div>
          ))}
          <div className="mt-1 flex items-center justify-between border-t border-zinc-100 pt-1.5 text-xs">
            <span className="font-semibold text-black">total</span>
            <span className="font-mono font-semibold text-black">{formatMicroUsd(ledger.totalUsd)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TokenLedger({ runs }: { runs: RunBlock[] }) {
  return (
    <div className="flex flex-col rounded-xl border border-zinc-200 bg-white">
      {runs.map((block, i) => (
        <div
          key={i}
          className={`p-3 ${i > 0 ? "border-t border-zinc-200" : ""}`}
        >
          <LedgerBlock
            ledger={block.ledger}
            header={`Run ${block.number} · ${block.optionLabel} · ${block.timeLabel}`}
            indentHeader
            recorded={block.recorded}
          />
        </div>
      ))}
    </div>
  );
}
