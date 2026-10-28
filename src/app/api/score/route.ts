import { and, eq } from "drizzle-orm";
import { z } from "zod";
import { getDb } from "@/db";
import { users, scores, attempts } from "@/db/schema";
import { listChallengeIds } from "@/lib/config";
import { readCookie, USER_COOKIE } from "@/lib/cookies";

/**
 * Record Score: persists the server-measured cost as the player's score.
 *
 * The body carries NO cost — the server records the cost from its own
 * attempt record (written by the SSE proxy when the run completed), so the
 * client never self-reports cost (#7 invariant). Recording the same hole
 * twice keeps the lowest score (golf: best round on a hole is your score).
 * The attempt is matched by (user, challenge, option): the user picks the
 * option whose run they want to keep, without re-running it (#2 steps 14–15).
 */
const ScoreBodySchema = z.object({
  challengeId: z.number().int().positive(),
  optionId: z.string().min(1),
});

export async function POST(request: Request): Promise<Response> {
  const cookieUserId = readCookie(request.headers.get("cookie"), USER_COOKIE);
  if (!cookieUserId) {
    return Response.json({ error: "no user" }, { status: 401 });
  }

  const raw = await request.json().catch(() => null);
  const parsed = ScoreBodySchema.safeParse(raw);
  if (!parsed.success) {
    return Response.json({ error: parsed.error.message }, { status: 400 });
  }

  const db = getDb();
  const [user] = await db.select().from(users).where(eq(users.id, cookieUserId));
  if (!user) {
    return Response.json({ error: "no user" }, { status: 401 });
  }

  const known = listChallengeIds();
  if (!known.includes(parsed.data.challengeId)) {
    return Response.json({ error: "unknown challenge" }, { status: 404 });
  }

  // the server's own record of the run — the only cost source, matched to
  // the option the user chose to keep
  const [attempt] = await db
    .select({ costUsd: attempts.costUsd })
    .from(attempts)
    .where(
      and(
        eq(attempts.userId, cookieUserId),
        eq(attempts.challengeId, parsed.data.challengeId),
        eq(attempts.optionId, parsed.data.optionId),
      ),
    )
    .limit(1);
  if (!attempt) {
    return Response.json(
      { error: "no practice swing taken for this option" },
      { status: 409 },
    );
  }
  // golf: recording the same hole again keeps the lowest score
  const [existingScore] = await db
    .select({ costUsd: scores.costUsd })
    .from(scores)
    .where(and(eq(scores.userId, cookieUserId), eq(scores.challengeId, parsed.data.challengeId)))
    .limit(1);
  if (existingScore && existingScore.costUsd <= attempt.costUsd) {
    return Response.json({ ok: true, kept: "existing (lowest)" });
  }

  if (existingScore) {
    await db
      .update(scores)
      .set({ costUsd: attempt.costUsd, recordedAt: Date.now() })
      .where(and(eq(scores.userId, cookieUserId), eq(scores.challengeId, parsed.data.challengeId)));
  } else {
    await db.insert(scores).values({
      userId: cookieUserId,
      challengeId: parsed.data.challengeId,
      costUsd: attempt.costUsd,
      recordedAt: Date.now(),
    });
  }

  return Response.json({ ok: true });
}
