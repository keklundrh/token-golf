# --- deps + build stage: compiles better-sqlite3, needs python3/make/g++ ---
FROM node:22-alpine AS builder
RUN apk add --no-cache python3 make g++ \
  && corepack enable \
  && corepack prepare pnpm@12.10.1 --activate
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# --- runtime ---
FROM node:22-alpine
RUN apk add --no-cache libc6-compat \
  && corepack enable \
  && corepack prepare pnpm@12.10.1 --activate
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./next.config.ts
COPY --from=builder /app/config ./config
CMD ["node_modules/.bin/next", "start"]
