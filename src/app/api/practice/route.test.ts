import { describe, it, expect } from "vitest";
import { POST } from "./route";
import { USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users } from "@/db/schema";


const TEST_USER_ID = "route-test-user";

function request(body: unknown, cookie?: string): Request {
  return new Request("http://localhost:3000/api/practice", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(cookie ? { cookie } : {}) },
    body: JSON.stringify(body),
  });
}

function userCookie(): string {
  return `${USER_COOKIE}=${TEST_USER_ID}`;
}

function ensureUser(): void {
  getDb()
    .insert(users)
    .values({ id: TEST_USER_ID, username: `route-test`, createdAt: Date.now() })
    .onConflictDoNothing()
    .run();
}



describe("POST /api/practice config error distinction", () => {
  it("returns 404 unknown challenge for a genuinely missing hole", async () => {
    ensureUser();
    const res = await POST(request({ challengeId: 999, optionId: "x" }, userCookie()));
    expect(res.status).toBe(404);
    const data = await res.json();
    expect(data.error).toBe("unknown challenge");
  });

  it("returns 500 Invalid config when a challenge yaml fails validation", async () => {
    // hole-998 in the env-config dir has thinking: "ultra" — invalid enum value.
    // Exercises the real loader's Invalid-config throw through the route's
    // message branch without touching the app's config or database.
    ensureUser();
    const res = await POST(request({ challengeId: 998, optionId: "a" }, userCookie()));
    expect(res.status).toBe(500);
    const data = await res.json();
    expect(data.error).toContain("Invalid config at");
    expect(data.error).toContain("challenge.yaml");
  });

  it("returns 401 for a missing user", async () => {
    const res = await POST(request({ challengeId: 1, optionId: "terse" }));
    expect(res.status).toBe(401);
  });
});
