import { describe, it, expect } from "vitest";
import { golfAnimationFrame, GOLF_ANIMATION_FRAMES, shouldShowWaitingAnimation } from "./golf-animation";

function frameRows(tick: number): string[] {
  return golfAnimationFrame(tick).split("\n");
}

describe("golfAnimationFrame", () => {
  it("shows the ball on the tee beside the golfer while addressing", () => {
    const rows = frameRows(0);
    expect(rows[4]).toContain("o/○");
    // ground line with the hole, ball not yet flying
    expect(rows[5]).toContain("◯");
  });

  it("peaks near the top row mid-flight", () => {
    const rows = frameRows(9);
    const ballRow = rows.findIndex((r) => r.includes("○"));
    expect(ballRow).toBeLessThanOrEqual(1);
  });

  it("traces a full arc: ball descends back to the ground line at the hole", () => {
    const rows = frameRows(14);
    const ballRow = rows.findIndex((r) => r.includes("○"));
    expect(ballRow).toBe(4);
    expect(rows[4].indexOf("○")).toBe(rows[5].indexOf("◯"));
  });

  it("ends holed: ball gone from the sky, hole marked with the holed ball", () => {
    const rows = frameRows(16);
    expect(rows.slice(0, 5).join("\n")).not.toContain("○");
    expect(rows[5]).toContain("◉");
  });

  it("is deterministic and loops with period GOLF_ANIMATION_FRAMES", () => {
    expect(golfAnimationFrame(0)).toBe(golfAnimationFrame(GOLF_ANIMATION_FRAMES));
    expect(golfAnimationFrame(9)).toBe(golfAnimationFrame(9));
    // negative ticks wrap rather than throw
    expect(golfAnimationFrame(-1)).toBe(golfAnimationFrame(GOLF_ANIMATION_FRAMES - 1));
  });

  it("keeps every frame the same shape: 5 sky rows + ground line", () => {
    for (let t = 0; t < GOLF_ANIMATION_FRAMES; t++) {
      expect(frameRows(t)).toHaveLength(6);
    }
  });
});

describe("shouldShowWaitingAnimation", () => {
  it("shows while practice is streaming and only the input segment exists", () => {
    expect(shouldShowWaitingAnimation(true, [{ kind: "input" }])).toBe(true);
  });

  it("hides as soon as the first model stream segment arrives", () => {
    expect(shouldShowWaitingAnimation(true, [{ kind: "input" }, { kind: "output" }])).toBe(false);
    expect(shouldShowWaitingAnimation(true, [{ kind: "input" }, { kind: "reasoning" }])).toBe(false);
    expect(shouldShowWaitingAnimation(true, [{ kind: "input" }, { kind: "tools" }])).toBe(false);
  });

  it("hides when practice is not streaming or the input has not arrived yet", () => {
    expect(shouldShowWaitingAnimation(false, [{ kind: "input" }])).toBe(false);
    expect(shouldShowWaitingAnimation(true, [])).toBe(false);
  });
});
