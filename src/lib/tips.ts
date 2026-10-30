import type { TokenUsage } from "./cost";
import type { ModelRates } from "./currency";

/**
 * Post-run tip per #9: a one-line "what just happened" summary derived ONLY
 * from the run's measured data and config rates — which option ran, which
 * model, where the money went (dominant cost category), and what to try
 * next. Same honesty rule as #5's ledger: never invented.
 */

export interface RunTipInput {
  optionLabel: string;
  modelId: string;
  rates: ModelRates;
  usage: TokenUsage;
  costs: { inputUsd: number; outputUsd: number; reasoningUsd: number; cacheReadUsd: number; cacheWriteUsd: number };
  /** Training-display flags (same rule as the ledger): thinking/cache
   * categories are considered only when the option's flag is set. */
  flags?: { thinking?: boolean; caching?: boolean };
}

interface Category {
  label: string;
  tokens: number;
  usd: number;
  rate: number;
  suggestion: string;
}

/**
 * Build the post-run tip line, e.g.
 * "Detailed explanation on anthropic/claude-sonnet-4-5: output tokens
 * dominated — 300 tok at 15 µ$/tok. Try a shorter output to cut it."
 */
export function buildRunTip({ optionLabel, modelId, rates, usage, costs, flags = {} }: RunTipInput): string {
  const categories: Category[] = [
    {
      label: "input",
      tokens: usage.inputTokens,
      usd: costs.inputUsd,
      rate: rates.inputPerMtok,
      suggestion: "a shorter prompt would cut the input cost",
    },
    {
      label: "output",
      tokens: usage.outputTokens,
      usd: costs.outputUsd,
      rate: rates.outputPerMtok,
      suggestion: "a shorter output would cut it",
    },
  ];
  if (flags.thinking && usage.reasoningTokens !== null && usage.reasoningTokens > 0 && rates.reasoningPerMtok !== null) {
    categories.push({
      label: "thinking",
      tokens: usage.reasoningTokens,
      usd: costs.reasoningUsd,
      rate: rates.reasoningPerMtok,
      suggestion: "a lower thinking effort would cut it",
    });
  }
  const cacheReadTokens = usage.cacheReadTokens ?? null;
  const cacheWriteTokens = usage.cacheWriteTokens ?? null;
  if (flags.caching && cacheReadTokens !== null && cacheReadTokens > 0) {
    categories.push({
      label: "cache read",
      tokens: cacheReadTokens,
      usd: costs.cacheReadUsd,
      rate: rates.cacheReadPerMtok ?? 0,
      suggestion: "cache reads are cheaper than fresh input — that's the saving",
    });
  }
  if (flags.caching && cacheWriteTokens !== null && cacheWriteTokens > 0) {
    categories.push({
      label: "cache write",
      tokens: cacheWriteTokens,
      usd: costs.cacheWriteUsd,
      rate: rates.cacheWritePerMtok ?? 0,
      suggestion: "cache writes cost more upfront but are cheaper on the next equivalent run",
    });
  }

  const dominant = categories.reduce((a, b) => (b.usd > a.usd ? b : a));
  const tokens = dominant.tokens.toLocaleString("en-US");
  return `${optionLabel} on ${modelId}: ${dominant.label} tokens dominated — ${tokens} tok at ${dominant.rate} µ$/tok. Try ${dominant.suggestion}.`;
}
