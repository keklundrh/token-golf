import { describe, it, expect } from "vitest";
import { OptionSchema } from "./config";

describe("OptionSchema thinking and skills fields", () => {
  it("accepts thinking flag", () => {
    const result = OptionSchema.safeParse({
      id: "a",
      label: "A",
      detail: "d",
      prompt: "p",
      thinking: true,
    });
    expect(result.success).toBe(true);
    if (result.success) expect(result.data.thinking).toBe(true);
  });

  it("accepts graded thinking modes low, medium, high", () => {
    for (const mode of ["low", "medium", "high"] as const) {
      const result = OptionSchema.safeParse({
        id: "a",
        label: "A",
        detail: "d",
        prompt: "p",
        thinking: mode,
      });
      expect(result.success).toBe(true);
      if (result.success) expect(result.data.thinking).toBe(mode);
    }
  });

  it("rejects unknown thinking mode strings", () => {
    const result = OptionSchema.safeParse({
      id: "a",
      label: "A",
      detail: "d",
      prompt: "p",
      thinking: "max",
    });
    expect(result.success).toBe(false);
  });

  it("accepts skills list", () => {
    const result = OptionSchema.safeParse({
      id: "a",
      label: "A",
      detail: "d",
      prompt: "p",
      skills: ["web-search"],
    });
    expect(result.success).toBe(true);
    if (result.success) expect(result.data.skills).toEqual(["web-search"]);
  });

  it("rejects empty skill id", () => {
    const result = OptionSchema.safeParse({
      id: "a",
      label: "A",
      detail: "d",
      prompt: "p",
      skills: [""],
    });
    expect(result.success).toBe(false);
  });

  it("stays backwards compatible without the new fields", () => {
    const result = OptionSchema.safeParse({
      id: "a",
      label: "A",
      detail: "d",
      prompt: "p",
    });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.thinking).toBeUndefined();
      expect(result.data.skills).toBeUndefined();
      expect(result.data.model).toBeUndefined();
    }
  });
});
