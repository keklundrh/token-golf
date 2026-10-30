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

export interface RunRecordUsage {
  inputTokens: number;
  outputTokens: number;
  reasoningTokens: number | null;
  toolTokens: number;
  toolCalls: number;
  inputUsd: number;
  outputUsd: number;
  reasoningUsd: number;
}

export interface RunRecord {
  optionId: string;
  optionLabel: string;
  timestamp: number;
  usage: RunRecordUsage;
  costUsd: number;
  recorded: boolean;
}

export function relativeTime(timestamp: number, now: number = Date.now()): string {
  const seconds = Math.floor((now - timestamp) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  return `${Math.floor(minutes / 60)}h ago`;
}

export interface RunBlock {
  number: number;
  optionLabel: string;
  timeLabel: string;
  recorded: boolean;
  ledger: LedgerRowData;
}
export function buildRunBlocks(runs: RunRecord[], now: number = Date.now()): RunBlock[] {
  // oldest first: Run 1 at the top, newest last (adjacent to the action buttons)
  return runs.map((run, i) => ({
    number: i + 1,
    optionLabel: run.optionLabel,
    timeLabel: relativeTime(run.timestamp, now),
    recorded: run.recorded,
    ledger: buildLedger(
      run.usage,
      {
        inputUsd: run.usage.inputUsd,
        outputUsd: run.usage.outputUsd,
        reasoningUsd: run.usage.reasoningUsd,
        totalUsd: run.costUsd,
      },
    ),
  }));
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
      label: "thinking",
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
