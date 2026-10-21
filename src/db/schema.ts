import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";

export const users = sqliteTable("users", {
  id: text("id").primaryKey(),
  username: text("username").notNull().unique(),
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
