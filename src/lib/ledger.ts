import type { TokenUsage } from "@/lib/cost";

export interface LedgerCategory {
  key: string;
  label: string;
  tokens: number;
  calls?: number;
  usd: number;
  colorVar: string;
}

export interface LedgerRowData {
  categories: LedgerCategory[];
  totalUsd: number;
}

export function buildLedger(
  usage: TokenUsage & { toolTokens: number; toolCalls: number },
  costs: { inputUsd: number; outputUsd: number; reasoningUsd: number; totalUsd: number },
): LedgerRowData {
  const categories: LedgerCategory[] = [
    {
      key: "input",
      label: "input",
      tokens: usage.inputTokens,
      usd: costs.inputUsd,
      colorVar: "--ledger-input",
    },
    {
      key: "output",
      label: "output",
      tokens: usage.outputTokens,
      usd: costs.outputUsd,
      colorVar: "--ledger-output",
    },
  ];
  if (usage.reasoningTokens !== null && usage.reasoningTokens > 0) {
    categories.push({
      key: "reasoning",
      label: "reasoning",
      tokens: usage.reasoningTokens,
      usd: costs.reasoningUsd,
      colorVar: "--ledger-reasoning",
    });
  }
  if (usage.toolCalls > 0) {
    categories.push({
      key: "tools",
      label: "tools",
      tokens: usage.toolTokens,
      calls: usage.toolCalls,
      usd: 0,
      colorVar: "--ledger-tools",
    });
  }
  return { categories, totalUsd: costs.totalUsd };
}
