import { readCookie, USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users, attempts } from "@/db/schema";
import { and, eq, sql } from "drizzle-orm";
import { loadChallenge, loadSkills } from "@/lib/config";
import { renderPracticeStream } from "@/lib/practice";
import { SPEND_CAP_USD } from "@/lib/cost";

export const maxDuration = 60;

/** Route handler per Next.js signature; config dir override via env for tests. */

export async function GET(request: Request): Promise<Response> {
  const userId = readCookie(request.headers.get("cookie"), USER_COOKIE);
  if (!userId) return Response.json({ error: "no user" }, { status: 401 });
  const challengeId = Number(new URL(request.url).searchParams.get("challengeId"));
  if (!Number.isInteger(challengeId) || challengeId <= 0) {
    return Response.json({ error: "invalid challengeId" }, { status: 400 });
  }
  const attemptRows = await getDb()
    .select({ optionId: attempts.optionId, costUsd: attempts.costUsd })
    .from(attempts)
    .where(and(eq(attempts.userId, userId), eq(attempts.challengeId, challengeId)))
    .orderBy(attempts.createdAt);
  return Response.json({ attempts: attemptRows });
}
export async function POST(request: Request): Promise<Response> {
  const configDir = process.env.PRACTICE_CONFIG_DIR;
  const userId = readCookie(request.headers.get("cookie"), USER_COOKIE);
  if (!userId) {
    return Response.json({ error: "no user" }, { status: 401 });
  }

  const db = getDb();
  const [user] = await db.select().from(users).where(eq(users.id, userId));
  if (!user) {
    return Response.json({ error: "no user" }, { status: 401 });
  }

  // spend cap over ACTUAL provider spend (attempts written by the proxy) —
  // unrecorded practice swings cost real money, so they count toward the cap (#7)
  const [spent] = await db
    .select({ total: sql<number>`CAST(COALESCE(SUM(${attempts.costUsd}), 0) AS REAL)` })
    .from(attempts)
    .where(eq(attempts.userId, userId));

  if (Number(spent.total) >= SPEND_CAP_USD) {
    return Response.json(
      { error: `spend cap reached ($${spent.total.toFixed(2)} of $${SPEND_CAP_USD.toFixed(2)})` },
      { status: 429 },
    );
  }

  let body: { challengeId?: number; optionId?: string };
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "invalid body" }, { status: 400 });
  }

  if (
    typeof body.challengeId !== "number" ||
    typeof body.optionId !== "string" ||
    body.optionId.length === 0
  ) {
    return Response.json({ error: "invalid body" }, { status: 400 });
  }

  let challenge;
  try {
    challenge = loadChallenge(body.challengeId, configDir);
  } catch (e) {
    if (e instanceof Error && e.message.startsWith("Invalid config at")) {
      return Response.json({ error: e.message }, { status: 500 });
    }
    return Response.json({ error: "unknown challenge" }, { status: 404 });
  }

  const option = challenge.options.find((o) => o.id === body.optionId);
  if (!option) {
    return Response.json({ error: "unknown option" }, { status: 404 });
  }

  // one attempt per option per challenge; different options remain runnable.
  // The 409 carries the existing attempt so a reloaded page can seed a
  // recordable state (the user can still record the option they already ran).
  const [existingAttempt] = await db
    .select({ optionId: attempts.optionId, costUsd: attempts.costUsd })
    .from(attempts)
    .where(
      and(
        eq(attempts.userId, userId),
        eq(attempts.challengeId, body.challengeId),
        eq(attempts.optionId, body.optionId),
      ),
    )
    .limit(1);
  if (existingAttempt) {
    return Response.json(
      {
        error: "practice swing already taken for this option",
        attempt: existingAttempt,
      },
      { status: 409 },
    );
  }
  const stream = renderPracticeStream({ challenge, option, skills: loadSkills(), userId });
  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
