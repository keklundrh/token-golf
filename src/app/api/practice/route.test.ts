import { describe, it, expect, vi, afterAll } from "vitest";
import { and, eq } from "drizzle-orm";
import { GET, POST } from "./route";
import { USER_COOKIE } from "@/lib/cookies";
import { getDb } from "@/db";
import { users, attempts } from "@/db/schema";

vi.mock("@/lib/practice", () => ({
  renderPracticeStream: () =>
    new ReadableStream<Uint8Array>({
      start(c) {
        c.enqueue(new TextEncoder().encode('data: {"type":"done"}\n\n'));
        c.close();
      },
    }),
}));

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

function seedAttempt(
  optionId: string,
  costUsd: number,
  challengeId = 1,
  tokens: { inputTokens?: number; outputTokens?: number; reasoningTokens?: number | null } = {},
): void {
  getDb()
    .insert(attempts)
    .values({
      userId: TEST_USER_ID,
      challengeId,
      optionId,
      costUsd,
      inputTokens: tokens.inputTokens ?? 0,
      outputTokens: tokens.outputTokens ?? 0,
      reasoningTokens: tokens.reasoningTokens ?? null,
      createdAt: Date.now(),
    })
    .run();
}

afterAll(() => {
  getDb().delete(attempts).where(eq(attempts.userId, TEST_USER_ID)).run();
});

describe("POST /api/practice one attempt per option", () => {
  it("returns 409 when the same option is run twice", async () => {
    ensureUser();
    seedAttempt("terse", 0.001);
    const res = await POST(request({ challengeId: 1, optionId: "terse" }, userCookie()));
    expect(res.status).toBe(409);
    const data = await res.json();
    expect(data.error).toBe("practice swing already taken for this option");
    expect(data.attempt.optionId).toBe("terse");
  });

  it("allows a different option to swing after an attempt exists", async () => {
    ensureUser();
    seedAttempt("terse", 0.001);
    const res = await POST(request({ challengeId: 1, optionId: "verbose" }, userCookie()));
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toContain("text/event-stream");
  });

  it("returns 429 when the spend cap is reached over attempts (not scores)", async () => {
    ensureUser();
    // scoped clean slate: the earlier test's leaked attempt must not count
    getDb()
      .delete(attempts)
      .where(and(eq(attempts.userId, TEST_USER_ID), eq(attempts.challengeId, 1)))
      .run();
    // attempts sum over the cap ($0.50 default); a lower recorded score must
    // not matter — the cap counts actual provider spend (#7)
    seedAttempt("terse", 0.30, 1);
    seedAttempt("verbose", 0.30, 1);
    const res = await POST(request({ challengeId: 1, optionId: "large-input" }, userCookie()));
    expect(res.status).toBe(429);
    const data = await res.json();
    expect(data.error).toContain("spend cap reached");
  });
});

describe("GET /api/practice returns all attempts", () => {
  it("returns every option's attempt oldest-first and empty when none", async () => {
    ensureUser();
    const base = "http://localhost:3000/api/practice?challengeId=1";
    // clean slate for this user+challenge (scoped — other workers share the DB)
    getDb()
      .delete(attempts)
      .where(and(eq(attempts.userId, TEST_USER_ID), eq(attempts.challengeId, 1)))
      .run();
    seedAttempt("terse", 0.001);
    seedAttempt("verbose", 0.002);
    const res = await GET(new Request(base, { headers: { cookie: userCookie() } }));
    const data = await res.json();
    expect(data.attempts).toEqual([
      {
        optionId: "terse",
        costUsd: 0.001,
        inputTokens: 0,
        outputTokens: 0,
        reasoningTokens: null,
        cacheReadTokens: null,
        cacheWriteTokens: null,
        inputUsd: 0,
        outputUsd: 0,
        reasoningUsd: 0,
        cacheReadUsd: 0,
        cacheWriteUsd: 0,
      },
      {
        optionId: "verbose",
        costUsd: 0.002,
        inputTokens: 0,
        outputTokens: 0,
        reasoningTokens: null,
        cacheReadTokens: null,
        cacheWriteTokens: null,
        inputUsd: 0,
        outputUsd: 0,
        reasoningUsd: 0,
        cacheReadUsd: 0,
        cacheWriteUsd: 0,
      },
    ]);
    // don't leak these seeds into other tests (scoped + shuffle-safe)
    getDb()
      .delete(attempts)
      .where(and(eq(attempts.userId, TEST_USER_ID), eq(attempts.challengeId, 1)))
      .run();
  });


  it("returns real per-category costs for persisted token counts", async () => {
    ensureUser();
    const base = "http://localhost:3000/api/practice?challengeId=1";
    getDb()
      .delete(attempts)
      .where(and(eq(attempts.userId, TEST_USER_ID), eq(attempts.challengeId, 1)))
      .run();
    // hole 1's terse option: anthropic/claude-sonnet-4-5 (in 3.00, out 15.00)
    seedAttempt("terse", 0.24, 1, { inputTokens: 20_000, outputTokens: 12_000 });

    const res = await GET(new Request(base, { headers: { cookie: userCookie() } }));
    const data = await res.json();
    expect(data.attempts).toHaveLength(1);
    const row = data.attempts[0];
    expect(row.inputTokens).toBe(20_000);
    expect(row.outputTokens).toBe(12_000);
    // computeCost at GET time: 20_000/1e6*3.00 = 0.06, 12_000/1e6*15.00 = 0.18
    expect(row.inputUsd).toBeCloseTo(0.06);
    expect(row.outputUsd).toBeCloseTo(0.18);
    expect(row.reasoningUsd).toBe(0);

    getDb()
      .delete(attempts)
      .where(and(eq(attempts.userId, TEST_USER_ID), eq(attempts.challengeId, 1)))
      .run();
  });
});
