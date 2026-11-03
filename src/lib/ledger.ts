import type { TokenUsage } from "@/lib/cost";

export interface LedgerCategory {
  key: string;
  label: string;
  tokens: number;
  calls?: number;
  usd: number;
  colorVar: string;
  /** Visual weight carries the cost story: "heavy" = expensive row,
   * "light" = cheap row (cache write vs read; per #4). */
  emphasis?: "heavy" | "light";
}

export interface LedgerRowData {
  categories: LedgerCategory[];
  totalUsd: number;
}

export interface RunRecordUsage {
  inputTokens: number;
  outputTokens: number;
  reasoningTokens: number | null;
  cacheReadTokens: number | null;
  cacheWriteTokens: number | null;
  toolTokens: number;
  toolCalls: number;
  inputUsd: number;
  outputUsd: number;
  reasoningUsd: number;
  cacheReadUsd: number;
  cacheWriteUsd: number;
}

export interface RunRecord {
  optionId: string;
  optionLabel: string;
  timestamp: number;
  usage: RunRecordUsage;
  costUsd: number;
  recorded: boolean;
  /** Training-display flags (per the user's rule): thinking/cache/tools
   * rows render only when the option's config flag is set. */
  flags?: { thinking?: boolean; caching?: boolean; tools?: boolean };
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
export function buildRunBlocks(
  runs: RunRecord[],
  now: number = Date.now(),
  price?: { input_per_mtok: number; cache_read_per_mtok?: number | null; cache_write_per_mtok?: number | null },
): RunBlock[] {
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
        cacheReadUsd: run.usage.cacheReadUsd,
        cacheWriteUsd: run.usage.cacheWriteUsd,
        totalUsd: run.costUsd,
      },
      run.flags,
      price,
    ),
  }));
}

/**
 * Cache row labels read as INPUT charges, not output (per #10): the old
 * "cache write"/"cache read" names were interpreted as output charges.
 * Ratios derive from the model's pricing; without cache pricing the
 * multiplier is omitted — never display one the charge doesn't reflect.
 */
export function cacheRowLabel(
  price: { input_per_mtok: number; cache_read_per_mtok?: number | null; cache_write_per_mtok?: number | null } | undefined,
  kind: "read" | "write",
): string {
  const rate = kind === "read" ? price?.cache_read_per_mtok : price?.cache_write_per_mtok;
  const noun = kind === "read" ? "cache hit" : "cache save";
  if (rate == null || !price?.input_per_mtok) return `input (${noun})`;
  const ratio = rate / price.input_per_mtok;
  return `input × ${Number.isInteger(ratio) ? ratio : Math.round(ratio * 100) / 100} (${noun})`;
}

export function buildLedger(
  usage: TokenUsage & {
    toolTokens: number;
    toolCalls: number;
    cacheReadTokens: number | null;
    cacheWriteTokens: number | null;
  },
  costs: {
    inputUsd: number;
    outputUsd: number;
    reasoningUsd: number;
    cacheReadUsd: number;
    cacheWriteUsd: number;
    totalUsd: number;
  },
  flags: { thinking?: boolean; caching?: boolean; tools?: boolean } = {},
  price?: { input_per_mtok: number; cache_read_per_mtok?: number | null; cache_write_per_mtok?: number | null },
): LedgerRowData {
  // The SDK's inputTokens INCLUDES cached tokens (verified in the provider
  // SDK sources): the input row must show only the tokens actually charged
  // at input rate, so the row's tok count and µ$ agree. Mirrors
  // computeCost, which subtracts unconditionally — an implicitly-caching
  // backend (OpenAI) reports cache tokens without a config flag, and the
  // flag only gates the read/write ROWS, not this math.
  const cachedTokens = (usage.cacheReadTokens ?? 0) + (usage.cacheWriteTokens ?? 0);
  const uncachedInputTokens = Math.max(0, usage.inputTokens - cachedTokens);
  const categories: LedgerCategory[] = [
    {
      key: "input",
      label: "input",
      tokens: uncachedInputTokens,
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
  // Training-display rule (per the user's decision, superseding #5's
  // render-when-reported rule): input and output are defaults, always
  // shown; thinking/cache/tools rows render only when the option's config
  // flag is set — an endpoint that reasons by default must not teach a
  // concept the challenge didn't author.
  if (flags.thinking && usage.reasoningTokens !== null && usage.reasoningTokens > 0) {
    categories.push({
      key: "reasoning",
      label: "thinking",
      tokens: usage.reasoningTokens,
      usd: costs.reasoningUsd,
      colorVar: "--ledger-reasoning",
    });
  }
  if (flags.caching && usage.cacheReadTokens !== null && usage.cacheReadTokens > 0) {
    categories.push({
      key: "cache-read",
      label: cacheRowLabel(price, "read"),
      tokens: usage.cacheReadTokens,
      usd: costs.cacheReadUsd,
      colorVar: "--ledger-cache-read",
      emphasis: "light",
    });
  }
  if (flags.caching && usage.cacheWriteTokens !== null && usage.cacheWriteTokens > 0) {
    categories.push({
      key: "cache-write",
      label: cacheRowLabel(price, "write"),
      tokens: usage.cacheWriteTokens,
      usd: costs.cacheWriteUsd,
      colorVar: "--ledger-cache-write",
      emphasis: "heavy",
    });
  }
  if (flags.tools && usage.toolCalls > 0) {
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
