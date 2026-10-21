import Database from "better-sqlite3";
import { drizzle, type BetterSQLite3Database } from "drizzle-orm/better-sqlite3";
import * as schema from "./schema";

export type Db = BetterSQLite3Database<typeof schema>;

const DB_PATH = process.env.DATABASE_PATH ?? "token-golf.db";

function createDb(): Db {
  const sqlite = new Database(DB_PATH);
  sqlite.pragma("journal_mode = WAL");
  sqlite.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      username TEXT NOT NULL UNIQUE,
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
