import { describe, it, expect } from "vitest";
import { loadHomepage } from "./config";

describe("homepage config content", () => {
  const hp = loadHomepage();

  it("has all sections the splash page renders", () => {
    expect(hp.title.length).toBeGreaterThan(0);
    expect(hp.intro.length).toBeGreaterThan(0);
    expect(hp.howToPlay.length).toBeGreaterThan(0);
    expect(hp.cta.label.length).toBeGreaterThan(0);
    expect(hp.cta.target).toMatch(/^\//);
  });

  it("has username pools for generation", () => {
    expect(hp.username.players.length).toBeGreaterThanOrEqual(5);
    expect(hp.username.courses.length).toBeGreaterThanOrEqual(5);
    expect(hp.username.colors).toEqual(
      expect.arrayContaining(["white", "black", "green", "yellow", "red"]),
    );
  });
});
