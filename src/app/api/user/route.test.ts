import { describe, it, expect, vi, afterAll } from "vitest";
import { eq, inArray } from "drizzle-orm";
import { POST } from "./route";
import { USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users } from "@/db/schema";

// tiny pool for the exhaustion test: 1 player x 1 course x 1 color x 1..999
// = 999 usernames — fast, deterministic, well within SQLite limits
const hpMock = vi.hoisted(() => ({
  loadHomepage: vi.fn(() => ({
    title: "Token Golf",
    intro: "intro",
    howToPlay: [],
    cta: { label: "Start Playing", target: "/hole/1" },
    username: {
      players: ["Tiger"],
      courses: ["Augusta"],
      colors: ["green"],
    },
  })),
}));

vi.mock("@/lib/config", () => ({
  loadHomepage: hpMock.loadHomepage,
}));

const USER_ID = "user-route-test";

function cookieFor(id: string): string {
  return `${USER_COOKIE}=${id}`;
}

afterAll(() => {
  getDb().delete(users).where(eq(users.id, USER_ID)).run();
});

describe("POST /api/user (identity)", () => {
  it("creates a user, sets the cookie, and returns the username", async () => {
    const res = await POST(new Request("http://localhost:3000/api/user", { method: "POST" }));
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.username).toMatch(/^[A-Za-z]+-[A-Za-z]+-[a-z]+-\d+$/);
    const setCookie = res.headers.get("set-cookie");
    expect(setCookie).toContain(`${USER_COOKIE}=`);
    expect(setCookie).toContain("HttpOnly");

    // cleanup for the created user
    getDb().delete(users).where(eq(users.id, data.userId)).run();
  });

  it("returns the same user when the existing cookie is sent", async () => {
    // create
    const first = await POST(new Request("http://localhost:3000/api/user", { method: "POST" }));
    const data = await first.json();
    getDb().delete(users).where(eq(users.id, data.userId)).run();

    // seed a known user, then reuse its cookie
    getDb()
      .insert(users)
      .values({ id: USER_ID, username: "Tiger-Augusta-green-1", createdAt: Date.now() })
      .onConflictDoNothing()
      .run();

    const res = await POST(
      new Request("http://localhost:3000/api/user", {
        method: "POST",
        headers: { cookie: cookieFor(USER_ID) },
      }),
    );
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.userId).toBe(USER_ID);
    expect(body.username).toBe("Tiger-Augusta-green-1");
    // existing identity: no Set-Cookie reissue
    expect(res.headers.get("set-cookie")).toBeNull();
  });

  it("returns 503 when the username space is exhausted", async () => {
    // fill the mocked pool: Tiger-Augusta-green-1..999
    const db = getDb();
    const values = Array.from({ length: 999 }, (_, i) => ({
      id: `exhaust-${i + 1}`,
      username: `Tiger-Augusta-green-${i + 1}`,
      createdAt: Date.now(),
    }));
    db.insert(users).values(values).onConflictDoNothing().run();

    const res = await POST(new Request("http://localhost:3000/api/user", { method: "POST" }));
    expect(res.status).toBe(503);
    const data = await res.json();
    expect(data.error).toBe("username space exhausted");

    // cleanup: the ids are sequential
    const ids = Array.from({ length: 999 }, (_, i) => `exhaust-${i + 1}`);
    db.delete(users).where(inArray(users.id, ids)).run();
  });
});
