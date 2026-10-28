"use client";

import { useEffect, useState } from "react";
import { golfAnimationFrame, GOLF_ANIMATION_FPS } from "@/lib/golf-animation";

/**
 * Waiting animation shown while the practice swing is in flight but no
 * model output has arrived yet (the input segment is already on screen).
 * Cycles the pure frame generator on a fixed interval.
 */
export default function GolfAnimation() {
  const [frame, setFrame] = useState(() => golfAnimationFrame(0));

  useEffect(() => {
    let tick = 0;
    const id = setInterval(() => {
      tick += 1;
      setFrame(golfAnimationFrame(tick));
    }, 1000 / GOLF_ANIMATION_FPS);
    return () => clearInterval(id);
  }, []);

  return (
    <pre className="text-xs leading-tight text-green-700" aria-hidden>
      {frame}
    </pre>
  );
}
