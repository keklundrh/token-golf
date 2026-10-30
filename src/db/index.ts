import Database from "better-sqlite3";
import { drizzle, type BetterSQLite3Database } from "drizzle-orm/better-sqlite3";
import * as schema from "./schema";

export type Db = BetterSQLite3Database<typeof schema>;

const DB_PATH = process.env.DATABASE_PATH ?? "token-golf.db";

function createDb(): Db {
  const sqlite = new Database(DB_PATH);
  // concurrent test workers share the temp DB file: wait for locks instead of
  // throwing SQLITE_BUSY; WAL switch takes an exclusive lock busy_timeout
  // doesn't cover, so a loser skips it (the winner already set WAL)
  sqlite.pragma("busy_timeout = 5000");
  try {
    sqlite.pragma("journal_mode = WAL");
  } catch {
    // another connection is mid-WAL-switch; its journal mode applies to the file
  }
  sqlite.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      username TEXT NOT NULL UNIQUE,
      created_at INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS attempts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL REFERENCES users(id),
      challenge_id INTEGER NOT NULL,
      option_id TEXT NOT NULL,
      cost_usd REAL NOT NULL,
      input_tokens INTEGER NOT NULL DEFAULT 0,
      output_tokens INTEGER NOT NULL DEFAULT 0,
      reasoning_tokens INTEGER,
      cache_read_tokens INTEGER,
      cache_write_tokens INTEGER,
      created_at INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS scores (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL REFERENCES users(id),
      challenge_id INTEGER NOT NULL,
      cost_usd REAL NOT NULL,
      recorded_at INTEGER NOT NULL
    );
  `);
  migrateAttempts(sqlite);
  return drizzle(sqlite, { schema });
}

// Existing DB files (Docker persistent volume, local dev db) predate the
// attempts usage columns: CREATE TABLE IF NOT EXISTS won't add them to a
// table that already exists. Idempotent ALTER TABLE guarded by a pragma
// column check.
// Exported for the migration test; getDb runs the migration automatically.
export function migrateAttemptsForTest(sqlite: Database.Database): void {
  migrateAttempts(sqlite);
}

function migrateAttempts(sqlite: Database.Database): void {
  const columns = new Set(
    (sqlite.pragma("table_info(attempts)") as Array<{ name: string }>).map((c) => c.name),
  );
  const add = (column: string, ddl: string) => {
    if (!columns.has(column)) sqlite.exec(`ALTER TABLE attempts ADD COLUMN ${ddl}`);
  };
  add("input_tokens", "input_tokens INTEGER NOT NULL DEFAULT 0");
  add("output_tokens", "output_tokens INTEGER NOT NULL DEFAULT 0");
  add("reasoning_tokens", "reasoning_tokens INTEGER");
  add("cache_read_tokens", "cache_read_tokens INTEGER");
  add("cache_write_tokens", "cache_write_tokens INTEGER");
}

let _db: Db | null = null;

export function getDb(): Db {
  if (!_db) _db = createDb();
  return _db;
}
