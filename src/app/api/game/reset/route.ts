import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { attempts, scores, users } from "@/db/schema";
import { readCookie, USER_COOKIE } from "@/lib/cookies";

/**
 * Start Playing starts a fresh round for the existing player identity: keep
 * the username/cookie, clear attempts (per-game swing availability and
 * spend-cap counter). Recorded scores are kept (#7) — best-per-hole handles
 * replays.
 */
export async function POST(request: Request): Promise<Response> {
  const userId = readCookie(request.headers.get("cookie"), USER_COOKIE);
  if (!userId) return Response.json({ error: "no user" }, { status: 401 });

  const db = getDb();
  const [user] = await db.select({ id: users.id }).from(users).where(eq(users.id, userId));
  if (!user) return Response.json({ error: "no user" }, { status: 401 });

  await db.delete(attempts).where(eq(attempts.userId, userId));

  return Response.json({ ok: true });
}
