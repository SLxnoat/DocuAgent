# ── Stage 1: Build ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

# Install dependencies first (cached layer)
COPY package*.json ./
RUN npm ci --ignore-scripts

# Copy source files and build production bundle
COPY . .
ARG VITE_API_BASE_URL=/api/v1
ARG VITE_API_HOST=localhost
ARG VITE_API_TOKEN=dev-secret-token
ARG VITE_ENABLE_PDF_EXPORT=true
ARG VITE_ENABLE_WEBSOCKET_CHAT=true
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_HOST=$VITE_API_HOST
ENV VITE_API_TOKEN=$VITE_API_TOKEN
ENV VITE_ENABLE_PDF_EXPORT=$VITE_ENABLE_PDF_EXPORT
ENV VITE_ENABLE_WEBSOCKET_CHAT=$VITE_ENABLE_WEBSOCKET_CHAT

RUN npm run build

# ── Stage 2: Serve via Nginx ────────────────────────────────────────────────
FROM nginx:1.27-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
