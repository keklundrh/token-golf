import { describe, it, expect } from "vitest";
import { generateUsername } from "./username";

const players = ["Tiger", "Rory"];
const courses = ["Augusta", "Pebble"];
const colors = ["green", "red"];

function seq(...values: number[]): () => number {
  let i = 0;
  return () => values[i++ % values.length];
}

describe("generateUsername", () => {
  it("produces player-course-color-number format", () => {
    const result = generateUsername(players, courses, colors, new Set(), () => 0);
    expect(result.username).toBe("Tiger-Augusta-green-1");
  });

  it("avoids existing usernames by incrementing the number", () => {
    const existing = new Set(["Tiger-Augusta-green-1", "Tiger-Augusta-green-2"]);
    const result = generateUsername(players, courses, colors, existing, () => 0);
    expect(result.username).toBe("Tiger-Augusta-green-3");
  });

  it("picks different names when random varies", () => {
    const result = generateUsername(players, courses, colors, new Set(), seq(0, 0.9, 0.9));
    expect(result.username).toBe("Tiger-Pebble-red-1");
  });

  it("throws when the space is exhausted", () => {
    const existing = new Set(
      Array.from({ length: 999 }, (_, i) => `Tiger-Augusta-green-${i + 1}`),
    );
    expect(() => generateUsername(players, courses, colors, existing, () => 0)).toThrow(
      "username space exhausted",
    );
  });
});
