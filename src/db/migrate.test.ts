import { describe, it, expect } from "vitest";
import Database from "better-sqlite3";
import { migrateAttemptsForTest } from "./index";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// getDb is a singleton bound to DATABASE_PATH at first call: test the
// migration by opening a pre-migration DB file directly.
describe("attempts usage migration", () => {
  it("adds usage columns to an existing pre-migration attempts table", () => {
    const dir = mkdtempSync(join(tmpdir(), "tg-migrate-"));
    const dbPath = join(dir, "legacy.db");
    const legacy = new Database(dbPath);
    legacy.exec(`
      CREATE TABLE users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        created_at INTEGER NOT NULL
      );
      CREATE TABLE attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL REFERENCES users(id),
        challenge_id INTEGER NOT NULL,
        option_id TEXT NOT NULL,
        cost_usd REAL NOT NULL,
        created_at INTEGER NOT NULL
      );
    `);
    legacy.close();

    // run the shipped migration path against the legacy file
    const db = new Database(dbPath);
    db.pragma("busy_timeout = 5000");
    const columnsBefore = new Set(
      (db.pragma("table_info(attempts)") as Array<{ name: string }>).map((c) => c.name),
    );
    expect(columnsBefore.has("input_tokens")).toBe(false);
    // exercise the same idempotent migration the loader runs
    migrateAttemptsForTest(db);
    const columns = new Set(
      (db.pragma("table_info(attempts)") as Array<{ name: string }>).map((c) => c.name),
    );
    for (const col of ["input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens", "cache_write_tokens"]) {
      expect(columns.has(col)).toBe(true);
    }

    // idempotent: running twice does not throw
    expect(() => migrateAttemptsForTest(db)).not.toThrow();

    // existing rows survive with 0-token defaults
    db.exec(`
      INSERT INTO users VALUES ('u1', 'Tiger-Augusta-green-1', 1);
      INSERT INTO attempts (user_id, challenge_id, option_id, cost_usd, created_at)
        VALUES ('u1', 1, 'terse', 0.001, 1);
    `);
    const row = db.prepare("SELECT input_tokens, output_tokens FROM attempts").get() as {
      input_tokens: number;
      output_tokens: number;
    };
    expect(row.input_tokens).toBe(0);
    expect(row.output_tokens).toBe(0);
    db.close();
  });
});
