import { describe, it, expect } from "vitest";
import { formatMicroUsd, MICROS_PER_USD, formatModelRates, type ModelRates } from "./currency";

describe("formatMicroUsd", () => {
  it("converts USD to integer micro-dollars", () => {
    expect(formatMicroUsd(0.000054)).toBe("54 µ$");
    expect(formatMicroUsd(0.000615)).toBe("615 µ$");
    expect(formatMicroUsd(0.0007)).toBe("700 µ$");
  });

  it("formats zero without decimals", () => {
    expect(formatMicroUsd(0)).toBe("0 µ$");
  });

  it("formats large amounts with thousands separators", () => {
    expect(formatMicroUsd(0.5)).toBe("500,000 µ$");
    expect(formatMicroUsd(1)).toBe("1,000,000 µ$");
  });

  it("rounds sub-micro precision", () => {
    expect(formatMicroUsd(0.0000004)).toBe("0 µ$");
    expect(formatMicroUsd(0.0000006)).toBe("1 µ$");
  });

  it("never emits fractional micro-dollars", () => {
    const out = formatMicroUsd(0.123456789);
    expect(out).toBe("123,457 µ$");
  });

  it("uses one million micro-dollars per USD", () => {
    expect(MICROS_PER_USD).toBe(1_000_000);
  });
});

describe("formatModelRates", () => {
  const sonnet: ModelRates = { inputPerMtok: 3.0, outputPerMtok: 15.0, reasoningPerMtok: 15.0 };
  const haiku: ModelRates = { inputPerMtok: 1.0, outputPerMtok: 5.0, reasoningPerMtok: 5.0 };
  const gptMini: ModelRates = { inputPerMtok: 0.25, outputPerMtok: 2.0, reasoningPerMtok: null };

  it("itemizes in/out/think rates in µ$/tok matching config values", () => {
    expect(formatModelRates(sonnet)).toBe("in 3 µ$/tok · out 15 µ$/tok · think 15 µ$/tok");
    expect(formatModelRates(haiku)).toBe("in 1 µ$/tok · out 5 µ$/tok · think 5 µ$/tok");
  });

  it("omits the think rate when reasoning pricing is null", () => {
    expect(formatModelRates(gptMini)).toBe("in 0.25 µ$/tok · out 2 µ$/tok");
  });

  it("keeps the YAML identity: per_mtok value equals the µ$/tok rate", () => {
    // per #8: USD/Mtok = µ$/tok, so the display value is the config value
    expect(formatModelRates(sonnet)).toContain("in 3 µ$/tok");
    expect(formatModelRates(sonnet)).not.toContain("in 3000");
    expect(formatModelRates(sonnet)).not.toContain("in 0.003");
  });
});
