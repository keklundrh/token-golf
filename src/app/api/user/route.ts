import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { users } from "@/db/schema";
import { generateUsername } from "@/lib/username";
import { loadHomepage } from "@/lib/config";
import { readCookie, USER_COOKIE } from "@/lib/cookies";

export async function POST(request: Request): Promise<Response> {
  const db = getDb();
  const cookieUserId = readCookie(request.headers.get("cookie"), USER_COOKIE);

  if (cookieUserId) {
    const [existing] = await db.select().from(users).where(eq(users.id, cookieUserId));
    if (existing) {
      return Response.json({ userId: existing.id, username: existing.username });
    }
  }

  const hp = loadHomepage();
  const existingUsernames = new Set(
    (await db.select({ username: users.username }).from(users)).map((r) => r.username),
  );

  let username: string;
  try {
    username = generateUsername(
      hp.username.players,
      hp.username.courses,
      hp.username.colors,
      existingUsernames,
    ).username;
  } catch {
    return Response.json({ error: "username space exhausted" }, { status: 503 });
  }

  const id = crypto.randomUUID();
  await db.insert(users).values({ id, username, createdAt: Date.now() });

  return Response.json(
    { userId: id, username },
    {
      headers: {
        "Set-Cookie": `${USER_COOKIE}=${id}; HttpOnly; Path=/; SameSite=Lax; Max-Age=86400`,
      },
    },
  );
}

