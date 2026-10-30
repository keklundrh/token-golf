import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";

export const users = sqliteTable("users", {
  id: text("id").primaryKey(),
  username: text("username").notNull().unique(),
  createdAt: integer("created_at").notNull(),
});

export const attempts = sqliteTable("attempts", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  userId: text("user_id")
    .notNull()
    .references(() => users.id),
  challengeId: integer("challenge_id").notNull(),
  optionId: text("option_id").notNull(),
  costUsd: real("cost_usd").notNull(),
  // measured token usage, persisted so a reloaded page can show the real
  // itemized ledger (not 0 tok) for runs it didn't see live
  inputTokens: integer("input_tokens").notNull().default(0),
  outputTokens: integer("output_tokens").notNull().default(0),
  reasoningTokens: integer("reasoning_tokens"),
  cacheReadTokens: integer("cache_read_tokens"),
  cacheWriteTokens: integer("cache_write_tokens"),
  createdAt: integer("created_at").notNull(),
});

export const scores = sqliteTable("scores", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  userId: text("user_id")
    .notNull()
    .references(() => users.id),
  challengeId: integer("challenge_id").notNull(),
  costUsd: real("cost_usd").notNull(),
  recordedAt: integer("recorded_at").notNull(),
});

export type User = typeof users.$inferSelect;
export type Score = typeof scores.$inferSelect;
