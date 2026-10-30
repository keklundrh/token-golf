import { loadPricing, type ModelPrice } from "@/lib/config";

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  reasoningTokens: number | null;
  cacheReadTokens?: number | null;
  cacheWriteTokens?: number | null;
}

export interface CostBreakdown {
  inputUsd: number;
  outputUsd: number;
  reasoningUsd: number;
  cacheReadUsd: number;
  cacheWriteUsd: number;
  totalUsd: number;
}

export function computeCost(model: string, usage: TokenUsage): CostBreakdown {
  const pricing = loadPricing();
  const price: ModelPrice | undefined = pricing.models[model];
  if (!price) {
    throw new Error(`no pricing for model: ${model}`);
  }

  // SDK semantics: inputTokens.total INCLUDES cached tokens (verified in
  // @ai-sdk/anthropic + @ai-sdk/openai source). Charge cached tokens at their
  // read/write rates and the remainder at the plain input rate — never both.
  const cacheReadTokens = usage.cacheReadTokens ?? 0;
  const cacheWriteTokens = usage.cacheWriteTokens ?? 0;
  const uncachedInputTokens = Math.max(
    0,
    usage.inputTokens - cacheReadTokens - cacheWriteTokens,
  );
  const cacheReadUsd =
    !cacheReadTokens || price.cache_read_per_mtok == null
      ? 0
      : (cacheReadTokens / 1_000_000) * price.cache_read_per_mtok;
  const cacheWriteUsd =
    !cacheWriteTokens || price.cache_write_per_mtok == null
      ? 0
      : (cacheWriteTokens / 1_000_000) * price.cache_write_per_mtok;
  // Without cache pricing configured, cached tokens fall back to the input
  // rate so the total still covers every token the provider charged.
  const inputUsd =
    (uncachedInputTokens / 1_000_000) * price.input_per_mtok +
    (price.cache_read_per_mtok == null ? cacheReadTokens : 0) / 1_000_000 * price.input_per_mtok +
    (price.cache_write_per_mtok == null ? cacheWriteTokens : 0) / 1_000_000 * price.input_per_mtok;
  const outputUsd = (usage.outputTokens / 1_000_000) * price.output_per_mtok;
  const reasoningUsd =
    usage.reasoningTokens === null || price.reasoning_per_mtok === null
      ? 0
      : (usage.reasoningTokens / 1_000_000) * price.reasoning_per_mtok;

  return {
    inputUsd,
    outputUsd,
    reasoningUsd,
    cacheReadUsd,
    cacheWriteUsd,
    totalUsd: inputUsd + outputUsd + reasoningUsd + cacheReadUsd + cacheWriteUsd,
  };
}

export function parseSpendCap(): number {
  const raw = process.env.SPEND_CAP_USD;
  if (raw === undefined) return 0.5;
  const parsed = Number(raw);
  return Number.isNaN(parsed) || parsed < 0 ? 0.5 : parsed;
}

export const SPEND_CAP_USD = parseSpendCap();
