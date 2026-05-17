# Start with Node.js base image
FROM node:20-slim AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
# ENV NEXT_TELEMETRY_DISABLED 1

# Provide non-public server env vars during build so libraries that validate presence
# don't fail the compilation step. Real values are injected at runtime via Compose.
ENV STRIPE_SECRET_KEY="__docker_build_dummy__"
ENV CLERK_SECRET_KEY="__docker_build_dummy__"
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_Y2FyZWZ1bC1jYXQtNDkuY2xlcmsuYWNjb3VudHMuZGV2JA"
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
# Uncomment the following line in case you want to disable telemetry during runtime.
# ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built assets from builder
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs

EXPOSE 3004

# Next defaults to 3000; this repo uses 3004 in docker-compose.
ENV PORT 3004

# Force bind + port explicitly so we don't rely on framework defaults.
CMD ["sh", "-c", "node node_modules/next/dist/bin/next start -H 0.0.0.0 -p ${PORT}"]
