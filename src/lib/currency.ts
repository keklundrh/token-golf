/**
 * Currency display: all UI dollar values render in micro-dollars (µ$;
 * 1 USD = 1,000,000 µ$). Stored values stay in real USD (config pricing,
 * DB cost_usd, computed costs) and are converted only here, at render time.
 */

/** Micro-dollars per USD. */
export const MICROS_PER_USD = 1_000_000;

/**
 * Format a USD amount as an integer micro-dollar string, e.g.
 * 0.000054 -> "54 µ$", 0.7 -> "700000 µ$". Sub-micro precision rounds.
 */
export function formatMicroUsd(usd: number): string {
  return `${Math.round(usd * MICROS_PER_USD).toLocaleString()} µ$`;
}

export interface ModelRates {
  inputPerMtok: number;
  outputPerMtok: number;
  reasoningPerMtok: number | null;
}

/**
 * Format a model's itemized rates for the pre-swing price line, e.g.
 * "in 3 µ$/tok · out 15 µ$/tok · thinking 15 µ$/tok". Reasoning rate omitted
 * when null (non-zero-only display rule per #5).
 *
 * USD-per-million-tok equals µ$-per-tok: the 1e6 factors cancel, so the
 * per_mtok value IS the µ$/tok rate (identity, per #8's rationale).
 */
export function formatModelRates(rates: ModelRates): string {
  const parts: string[] = [
    `in ${rates.inputPerMtok} µ$/tok`,
    `out ${rates.outputPerMtok} µ$/tok`,
  ];
  if (rates.reasoningPerMtok !== null) {
    parts.push(`thinking ${rates.reasoningPerMtok} µ$/tok`);
  }
  return parts.join(" · ");
}
