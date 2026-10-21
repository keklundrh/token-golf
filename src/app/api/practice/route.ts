import { readCookie, USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users, scores } from "@/db/schema";
import { eq, sql } from "drizzle-orm";
import { loadChallenge, loadSkills } from "@/lib/config";
import { renderPracticeStream } from "@/lib/practice";
import { SPEND_CAP_USD } from "@/lib/cost";

export const maxDuration = 60;

export async function POST(request: Request): Promise<Response> {
  const userId = readCookie(request.headers.get("cookie"), USER_COOKIE);
  if (!userId) {
    return Response.json({ error: "no user" }, { status: 401 });
  }

  const db = getDb();
  const [user] = await db.select().from(users).where(eq(users.id, userId));
  if (!user) {
    return Response.json({ error: "no user" }, { status: 401 });
  }

  const [spent] = await db
    .select({ total: sql<number>`CAST(COALESCE(SUM(${scores.costUsd}), 0) AS REAL)` })
    .from(scores)
    .where(eq(scores.userId, userId));

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
    challenge = loadChallenge(body.challengeId);
  } catch {
    return Response.json({ error: "unknown challenge" }, { status: 404 });
  }

  const option = challenge.options.find((o) => o.id === body.optionId);
  if (!option) {
    return Response.json({ error: "unknown option" }, { status: 404 });
  }

  const stream = renderPracticeStream({ challenge, option, skills: loadSkills() });
  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
