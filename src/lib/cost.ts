import { loadPricing, type ModelPrice } from "@/lib/config";

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  reasoningTokens: number | null;
}

export interface CostBreakdown {
  inputUsd: number;
  outputUsd: number;
  reasoningUsd: number;
  totalUsd: number;
}

export function computeCost(model: string, usage: TokenUsage): CostBreakdown {
  const pricing = loadPricing();
  const price: ModelPrice | undefined = pricing.models[model];
  if (!price) {
    throw new Error(`no pricing for model: ${model}`);
  }

  const inputUsd = (usage.inputTokens / 1_000_000) * price.input_per_mtok;
  const outputUsd = (usage.outputTokens / 1_000_000) * price.output_per_mtok;
  const reasoningUsd =
    usage.reasoningTokens === null || price.reasoning_per_mtok === null
      ? 0
      : (usage.reasoningTokens / 1_000_000) * price.reasoning_per_mtok;

  return {
    inputUsd,
    outputUsd,
    reasoningUsd,
    totalUsd: inputUsd + outputUsd + reasoningUsd,
  };
}

export const SPEND_CAP_USD = Number(process.env.SPEND_CAP_USD ?? 0.5);
