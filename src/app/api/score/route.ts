import { eq } from "drizzle-orm";
import { z } from "zod";
import { getDb } from "@/db";
import { users, scores } from "@/db/schema";
import { listChallengeIds } from "@/lib/config";
import { readCookie, USER_COOKIE } from "@/lib/cookies";

export const dynamic = "force-dynamic";

const ScoreBodySchema = z.object({
  challengeId: z.number().int().positive(),
  costUsd: z.number().nonnegative(),
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

  await db.insert(scores).values({
    userId: cookieUserId,
    challengeId: parsed.data.challengeId,
    costUsd: parsed.data.costUsd,
    recordedAt: Date.now(),
  });

  return Response.json({ ok: true });
}

