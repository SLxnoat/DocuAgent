# ==============================================================================
# DocuAgent AI — Production Frontend Dockerfile
# Multi-stage optimized build: Node 20 builder -> Nginx Alpine static server
# ==============================================================================

# Stage 1: Build static distribution
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies using clean install
COPY package*.json ./
RUN npm ci

# Copy frontend source
COPY . .

# Build production assets
ARG VITE_API_URL=/api/v1
ARG VITE_WS_URL=/api/v1/ws
ENV VITE_API_URL=$VITE_API_URL \
    VITE_WS_URL=$VITE_WS_URL

RUN npm run build

# Stage 2: Serve using hardened Nginx
FROM nginx:1.27-alpine AS production

# Remove default configuration
RUN rm -rf /etc/nginx/conf.d/*

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
