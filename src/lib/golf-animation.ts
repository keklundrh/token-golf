/**
 * Pure frame generator for the practice-swing waiting animation:
 * the golfer addresses the ball, swings, the ball flies a full arc
 * from the tee to the hole, and drops in.
 *
 * Deterministic: frame(tick) depends only on tick, so tests can step
 * through the whole loop and the client can cycle it on an interval.
 */

export const GOLF_ANIMATION_FPS = 8;

// 22 frames: 0-5 address (ball on tee), 6 swing, 7-14 flight arc,
// 15 ball above the hole, 16-21 ball in the hole before looping.
export const GOLF_ANIMATION_FRAMES = 22;

const WIDTH = 28;

/**
 * Pure render decision: repeat the animation after the input dump until the
 * first model stream segment arrives. The stream replaces the animation.
 */
export function shouldShowWaitingAnimation(
  streaming: boolean,
  segments: ReadonlyArray<{ kind: string }>,
): boolean {
  return streaming && segments.length === 1 && segments[0].kind === "input";
}

const HOLE_COL = 24;
const TEE_COL = 3;
const APEX_ROW = 0;
const TEE_ROW = 4;
const GROUND = "·";
const HOLE = "◯";
const BALL = "○";
const HOLED = "◉";

/** 5 sky rows + ground line with the hole; ball and golfer placed by phase. */
function scene(ball: { col: number; row: number } | null, golfer: boolean): string {
  const rows: string[][] = Array.from({ length: 5 }, () => Array<string>(WIDTH).fill(" "));
  if (ball) rows[ball.row][ball.col] = BALL;
  if (golfer) {
    // golfer stands on the tee line, club beside the ball
    rows[TEE_ROW][1] = "o";
    rows[TEE_ROW][2] = "/";
  }
  rows.push(Array.from({ length: WIDTH }, (_, i) => (i === HOLE_COL ? HOLE : GROUND)));
  return rows.map((r) => r.join("")).join("\n");
}

/** Same-height scene with the holed ball (◉) where the hole was, golfer gone. */
function holedScene(): string {
  const sky = Array.from({ length: 5 }, () => " ".repeat(WIDTH));
  const ground = Array.from({ length: WIDTH }, (_, i) => (i === HOLE_COL ? HOLED : GROUND)).join("");
  return [...sky, ground].join("\n");
}

/**
 * Deterministic frame for a given tick; loops with period GOLF_ANIMATION_FRAMES.
 * Flight is a sine arc: TEE_ROW at launch and landing, APEX_ROW mid-flight.
 */
export function golfAnimationFrame(tick: number): string {
  const t = ((tick % GOLF_ANIMATION_FRAMES) + GOLF_ANIMATION_FRAMES) % GOLF_ANIMATION_FRAMES;
  if (t <= 5) return scene({ col: TEE_COL, row: TEE_ROW }, true); // address
  if (t === 6) return scene(null, true); // swing, ball just struck
  if (t <= 14) {
    const f = (t - 7) / 7; // 0..1 across the flight
    const col = Math.round(TEE_COL + f * (HOLE_COL - TEE_COL));
    const row = Math.round(TEE_ROW - (TEE_ROW - APEX_ROW) * Math.sin(Math.PI * f));
    return scene({ col, row }, true);
  }
  if (t === 15) return scene({ col: HOLE_COL, row: TEE_ROW }, true); // above the hole
  return holedScene(); // t 16-21: in the hole, hold before looping
}
