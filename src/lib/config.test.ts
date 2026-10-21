import { describe, it, expect } from "vitest";
import {
  HomepageSchema,
  ChallengeSchema,
  PricingSchema,
  loadHomepage,
  loadChallenge,
  loadPricing,
  listChallengeIds,
  HOLE_DIR,
} from "./config";

describe("config schemas", () => {
  it("accepts valid homepage config", () => {
    const result = HomepageSchema.safeParse({
      title: "T",
      intro: "I",
      howToPlay: ["a"],
      cta: { label: "L", target: "/x" },
      username: { players: ["P"], courses: ["C"], colors: ["red"] },
    });
    expect(result.success).toBe(true);
  });

  it("rejects homepage config missing username pool", () => {
    const result = HomepageSchema.safeParse({
      title: "T",
      intro: "I",
      howToPlay: ["a"],
      cta: { label: "L", target: "/x" },
    });
    expect(result.success).toBe(false);
  });

  it("rejects challenge with no options", () => {
    const result = ChallengeSchema.safeParse({
      id: 1,
      par: 3,
      question: "Q",
      model: "m",
      options: [],
    });
    expect(result.success).toBe(false);
  });

  it("rejects negative price", () => {
    const result = PricingSchema.safeParse({
      models: { m: { input_per_mtok: -1, output_per_mtok: 2, reasoning_per_mtok: null } },
    });
    expect(result.success).toBe(false);
  });

  it("accepts null reasoning price", () => {
    const result = PricingSchema.safeParse({
      models: { m: { input_per_mtok: 1, output_per_mtok: 2, reasoning_per_mtok: null } },
    });
    expect(result.success).toBe(true);
  });
});

describe("config loader", () => {
  it("loads real homepage.yaml from repo config", () => {
    const hp = loadHomepage();
    expect(hp.title).toBe("Token Golf");
    expect(hp.username.players.length).toBeGreaterThan(0);
    expect(hp.username.colors).toContain("green");
  });

  it("loads hole 1 challenge", () => {
    const ch = loadChallenge(1);
    expect(ch.id).toBe(1);
    expect(ch.options.length).toBeGreaterThanOrEqual(2);
    expect(ch.options.every((o) => o.prompt.length > 0)).toBe(true);
  });

  it("throws on missing hole", () => {
    expect(() => loadChallenge(999)).toThrow();
  });

  it("loads pricing with per-model entries", () => {
    const p = loadPricing();
    expect(Object.keys(p.models).length).toBeGreaterThanOrEqual(1);
  });

  it("discovers hole-001 directory", () => {
    expect(listChallengeIds()).toContain(1);
    expect(HOLE_DIR(7)).toBe("hole-007");
  });
});
