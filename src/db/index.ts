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
  return drizzle(sqlite, { schema });
}

let _db: Db | null = null;

export function getDb(): Db {
  if (!_db) _db = createDb();
  return _db;
}
