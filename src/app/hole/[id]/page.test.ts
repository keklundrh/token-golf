import { describe, it, expect } from "vitest";
import { buildOptionRates } from "./page";
import type { ModelPrice } from "@/lib/config";

const pricing: Record<string, ModelPrice> = {
  "anthropic/claude-sonnet-4-5": {
    input_per_mtok: 3,
    output_per_mtok: 15,
    reasoning_per_mtok: 15,
  },
  "anthropic/claude-haiku-4-5": {
    input_per_mtok: 1,
    output_per_mtok: 5,
    reasoning_per_mtok: 5,
  },
};

describe("buildOptionRates", () => {
  it("keys rates by option id so default-model options do not collide", () => {
    const rates = buildOptionRates(
      [{ id: "verbose" }, { id: "balanced" }, { id: "terse" }],
      "anthropic/claude-sonnet-4-5",
      pricing,
    );

    expect(Object.keys(rates).sort()).toEqual(["balanced", "terse", "verbose"]);
    expect(rates.verbose.modelId).toBe("anthropic/claude-sonnet-4-5");
    expect(rates.balanced.rates).toEqual({
      inputPerMtok: 3,
      outputPerMtok: 15,
      reasoningPerMtok: 15,
    });
  });

  it("uses option-level model overrides when present", () => {
    const rates = buildOptionRates(
      [{ id: "driver" }, { id: "putter", model: "anthropic/claude-haiku-4-5" }],
      "anthropic/claude-sonnet-4-5",
      pricing,
    );

    expect(rates.driver.modelId).toBe("anthropic/claude-sonnet-4-5");
    expect(rates.putter.modelId).toBe("anthropic/claude-haiku-4-5");
    expect(rates.putter.rates).toEqual({
      inputPerMtok: 1,
      outputPerMtok: 5,
      reasoningPerMtok: 5,
    });
  });

  it("throws a clean error when a model has no pricing entry", () => {
    expect(() =>
      buildOptionRates([{ id: "x", model: "openai/nope" }], "anthropic/claude-sonnet-4-5", pricing),
    ).toThrow("no pricing for model: openai/nope");
  });
});

