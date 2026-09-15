# Deployment & Operations Guide

**Document ID:** DOC-007  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** DevOps Engineers, SRE, System Administrators

---

## Table of Contents

1. [Infrastructure Overview](#1-infrastructure-overview)
2. [Prerequisites](#2-prerequisites)
3. [Environment Configuration](#3-environment-configuration)
4. [Backend Service Deployment](#4-backend-service-deployment)
5. [Frontend Deployment](#5-frontend-deployment)
6. [Database & Cache Setup](#6-database--cache-setup)
7. [Ollama Cloud Configuration](#7-ollama-cloud-configuration)
8. [Docker Compose Setup](#8-docker-compose-setup)
9. [Celery Worker Configuration](#9-celery-worker-configuration)
10. [Nginx Reverse Proxy Configuration](#10-nginx-reverse-proxy-configuration)
11. [Health Checks & Monitoring](#11-health-checks--monitoring)
12. [Scaling Strategy](#12-scaling-strategy)
13. [Backup & Recovery](#13-backup--recovery)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Infrastructure Overview

DocuAgent AI is deployed as a set of containerized services orchestrated via Docker Compose (single-server) or Kubernetes (production clusters).

### 1.1 Service Map

```
┌─────────────────────────────────────────────────────────────┐
│                      INGRESS LAYER                          │
│                   Nginx (Port 80 / 443)                     │
│          TLS Termination · Reverse Proxy · Static Hosting   │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────┐       ┌─────────────────────────────┐
│  FRONTEND SERVICE     │       │  BACKEND SERVICE             │
│  React SPA (Nginx)    │       │  FastAPI (Uvicorn/Gunicorn)  │
│  Port: 3000 (internal)│       │  Port: 8000 (internal)       │
└───────────────────────┘       └──────────────┬──────────────┘
                                               │
                              ┌────────────────┼───────────────────┐
                              │                │                   │
                              ▼                ▼                   ▼
                    ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐
                    │   REDIS     │  │  CELERY      │  │  PLAYWRIGHT     │
                    │   Service   │  │  WORKERS     │  │  (inside Worker │
                    │  Port: 6379 │  │  (N workers) │  │   processes)    │
                    └─────────────┘  └──────────────┘  └─────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  OLLAMA CLOUD API   │
                    │  (External Service) │
                    └─────────────────────┘
```

### 1.2 Port Map

| Service                    | Internal Port | External (via Nginx)              |
| -------------------------- | ------------- | --------------------------------- |
| Nginx                      | 80, 443       | 80, 443                           |
| FastAPI                    | 8000          | `/api/*` (proxied)                |
| React SPA                  | 3000          | `/` (served by Nginx)             |
| Redis                      | 6379          | Internal only                     |
| Celery Flower (monitoring) | 5555          | `/flower/*` (proxied, auth-gated) |

---

## 2. Prerequisites

### 2.1 System Requirements

| Component      | Minimum          | Recommended      |
| -------------- | ---------------- | ---------------- |
| CPU            | 4 vCPUs          | 8 vCPUs          |
| RAM            | 8 GB             | 16 GB            |
| Disk           | 50 GB SSD        | 200 GB SSD       |
| OS             | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Docker         | 24.0+            | Latest           |
| Docker Compose | 2.20+            | Latest           |
| Python         | 3.11+            | 3.11+            |
| Node.js        | 18+              | 20 LTS           |

### 2.2 Network Requirements

| Destination                  | Protocol   | Port    | Purpose               |
| ---------------------------- | ---------- | ------- | --------------------- |
| Ollama Cloud endpoint        | HTTPS      | 443     | LLM inference         |
| Staging application (target) | HTTP/HTTPS | 80, 443 | Playwright automation |
| Redis (internal)             | TCP        | 6379    | Task queue & state    |

### 2.3 Software Installation

```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs

# Install Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Install Playwright system dependencies
sudo apt-get install -y \
  libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
  libxrandr2 libgbm1 libxss1 libasound2 libpangocairo-1.0-0
```

---

## 3. Environment Configuration

### 3.1 Backend Environment Variables

```bash
# /backend/.env

# Application
APP_ENV=production
APP_PORT=8000
SECRET_KEY=your-cryptographically-secure-secret-key-here
API_TOKEN=your-bearer-token-for-client-authentication

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_TTL_HOURS=24

# Ollama Cloud
OLLAMA_BASE_URL=https://your-ollama-cloud-endpoint.example.com
OLLAMA_PRIMARY_MODEL=llama3.3:70b
OLLAMA_FAST_MODEL=qwen2.5:72b
OLLAMA_TIMEOUT_SECONDS=120
OLLAMA_MAX_RETRIES=3

# Playwright
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_VIEWPORT_WIDTH=1440
PLAYWRIGHT_VIEWPORT_HEIGHT=900
PLAYWRIGHT_SELECTOR_TIMEOUT_MS=10000
PLAYWRIGHT_NAVIGATION_TIMEOUT_MS=30000
PLAYWRIGHT_SCREENSHOT_DIR=/app/assets

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
CELERY_WORKER_CONCURRENCY=5
CELERY_TASK_TIMEOUT_SECONDS=600

# Export
WEASYPRINT_ENABLED=true
PANDOC_ENABLED=true
EXPORT_DIR=/app/exports
```

### 3.2 Frontend Environment Variables

```bash
# /frontend/.env.production

VITE_API_BASE_URL=https://docuagent.yourdomain.com/api/v1
VITE_API_HOST=docuagent.yourdomain.com
VITE_API_TOKEN=your-bearer-token-for-client-authentication
VITE_ENABLE_PDF_EXPORT=true
VITE_ENABLE_WEBSOCKET_CHAT=true
```

---

## 4. Backend Service Deployment

### 4.1 Python Virtual Environment Setup

```bash
cd /app/backend

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium
```

### 4.2 requirements.txt (Core Dependencies)

```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
gunicorn>=21.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# Agent Framework
langgraph>=0.1.0
langchain-core>=0.2.0
langchain-ollama>=0.1.0

# Browser Automation
playwright>=1.40.0

# Task Queue
celery>=5.3.0
redis>=5.0.0

# Export
weasyprint>=60.0
pypandoc>=1.13

# Utilities
httpx>=0.25.0
aiofiles>=23.0.0
Pillow>=10.0.0
```

### 4.3 Running the FastAPI Server

**Development:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production (Gunicorn + Uvicorn workers):**

```bash
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 5 \
  --log-level info \
  --access-logfile /var/log/docuagent/access.log \
  --error-logfile /var/log/docuagent/error.log
```

---

## 5. Frontend Deployment

```bash
cd /app/frontend

# Install dependencies
npm ci --production=false

# Build production bundle
npm run build

# Output: /app/frontend/dist/
# Serve via Nginx static hosting (see Section 10)
```

---

## 6. Database & Cache Setup

### 6.1 Redis Configuration

Redis serves dual purpose: Celery task broker and LangGraph state checkpointer.

```bash
# /etc/redis/redis.conf (key settings)
bind 0.0.0.0
port 6379
requirepass your-redis-password
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1      # Persist to disk every 15 minutes if 1+ key changed
appendonly yes  # Write-ahead log for durability
```

### 6.2 Redis Database Allocation

| DB Index | Purpose                     | TTL              |
| -------- | --------------------------- | ---------------- |
| `0`      | LangGraph state checkpoints | 24 hours         |
| `1`      | Celery task broker          | Auto (by Celery) |
| `2`      | Celery result backend       | 1 hour           |
| `3`      | SSE PubSub channels         | Session-duration |

---

## 7. Ollama Cloud Configuration

### 7.1 API Endpoint Validation

```bash
# Test Ollama Cloud connectivity
curl -X POST "${OLLAMA_BASE_URL}/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.3:70b",
    "prompt": "Hello",
    "stream": false
  }'

# Expected: {"response": "...", "done": true}
```

### 7.2 Model Pull (if self-hosted Ollama)

```bash
# Pull required models
ollama pull llama3.3:70b
ollama pull qwen2.5:72b

# Verify models are available
ollama list
```

---

## 8. Docker Compose Setup

```yaml
# docker-compose.yml

version: "3.9"

services:
  # Redis — Task Queue & State Persistence
  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server /etc/redis/redis.conf
    volumes:
      - ./config/redis.conf:/etc/redis/redis.conf
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379" # Bind to localhost only
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    env_file: ./backend/.env
    volumes:
      - screenshot_assets:/app/assets
      - export_files:/app/exports
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    restart: always
    env_file: ./backend/.env
    command: celery -A app.tasks worker --loglevel=info --concurrency=5
    volumes:
      - screenshot_assets:/app/assets
      - export_files:/app/exports
    depends_on:
      - redis
      - backend
    deploy:
      replicas: 2 # Scale workers horizontally

  # Celery Flower (monitoring dashboard)
  flower:
    image: mher/flower:2.0
    restart: always
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - FLOWER_BASIC_AUTH=admin:secure_flower_password
    ports:
      - "127.0.0.1:5555:5555"
    depends_on:
      - redis

  # Frontend (served by Nginx)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    volumes:
      - frontend_dist:/usr/share/nginx/html:ro
    ports:
      - "127.0.0.1:3000:3000"

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/ssl:/etc/nginx/ssl:ro
      - frontend_dist:/usr/share/nginx/html:ro
      - screenshot_assets:/usr/share/nginx/assets:ro
    depends_on:
      - backend
      - frontend

volumes:
  redis_data:
  screenshot_assets:
  export_files:
  frontend_dist:
```

**Start all services:**

```bash
docker compose up -d
docker compose logs -f  # Tail logs
docker compose ps       # Check service status
```

---

## 9. Celery Worker Configuration

### 9.1 Task Routing

```python
# app/celery_config.py

CELERY_TASK_ROUTES = {
    'app.tasks.generate_manual': {'queue': 'generation'},
    'app.tasks.recapture_step':  {'queue': 'capture'},
    'app.tasks.export_document': {'queue': 'export'},
}

CELERY_WORKER_QUEUES = {
    'generation': {'concurrency': 3},
    'capture':    {'concurrency': 5},   # More workers for Playwright capture
    'export':     {'concurrency': 2},
}
```

### 9.2 Worker Launch (per queue type)

```bash
# Generation workers
celery -A app.tasks worker -Q generation --concurrency=3 --loglevel=info

# Capture workers (Playwright)
celery -A app.tasks worker -Q capture --concurrency=5 --loglevel=info

# Export workers
celery -A app.tasks worker -Q export --concurrency=2 --loglevel=info
```

---

## 10. Nginx Reverse Proxy Configuration

```nginx
# /config/nginx.conf

events { worker_connections 1024; }

http {

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    # Upstream services
    upstream backend  { server backend:8000; }
    upstream flower   { server flower:5555; }

    server {
        listen 80;
        server_name docuagent.yourdomain.com;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name docuagent.yourdomain.com;

        ssl_certificate     /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         HIGH:!aNULL:!MD5;

        # Frontend SPA
        root /usr/share/nginx/html;
        index index.html;
        location / {
            try_files $uri $uri/ /index.html;  # React SPA fallback routing
        }

        # Backend API
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_read_timeout 300s;   # Allow long-running SSE connections
        }

        # SSE Streaming — disable buffering for real-time delivery
        location /api/v1/stream/ {
            proxy_pass http://backend;
            proxy_set_header Connection '';
            proxy_http_version 1.1;
            proxy_buffering off;
            proxy_cache off;
            proxy_read_timeout 600s;
            chunked_transfer_encoding on;
        }

        # WebSocket Chat
        location /api/v1/ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 3600s;   # 1 hour WebSocket keep-alive
        }

        # Screenshot Assets
        location /assets/ {
            alias /usr/share/nginx/assets/;
            expires 1h;
            add_header Cache-Control "public, no-transform";
        }

        # Celery Flower (auth-protected)
        location /flower/ {
            proxy_pass http://flower;
            auth_basic "DocuAgent Monitoring";
            auth_basic_user_file /etc/nginx/.htpasswd;
        }
    }
}
```

---

## 11. Health Checks & Monitoring

### 11.1 Service Health Endpoints

| Service          | Health Check URL                   | Expected Response  |
| ---------------- | ---------------------------------- | ------------------ |
| FastAPI Backend  | `GET /health`                      | `{"status": "ok"}` |
| Redis            | `redis-cli ping`                   | `PONG`             |
| Celery Workers   | `celery -A app.tasks inspect ping` | Worker heartbeat   |
| Flower Dashboard | `http://localhost:5555`            | Web UI             |

### 11.2 Recommended Monitoring Stack

| Tool                       | Purpose                                                                                  |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| **Prometheus**             | Metrics collection (FastAPI `/metrics` endpoint via `prometheus-fastapi-instrumentator`) |
| **Grafana**                | Metrics visualization dashboards                                                         |
| **Celery Flower**          | Celery task monitoring and worker management                                             |
| **Uptime Robot / Pingdom** | External uptime monitoring                                                               |
| **Loki + Promtail**        | Centralized log aggregation                                                              |

### 11.3 Key Metrics to Monitor

| Metric                      | Alert Threshold         |
| --------------------------- | ----------------------- |
| API response time (p95)     | > 2 seconds             |
| Generation job success rate | < 95%                   |
| Celery queue depth          | > 20 pending tasks      |
| Redis memory usage          | > 80% of `maxmemory`    |
| Failed Playwright captures  | > 20% of total captures |
| Ollama API error rate       | > 5%                    |

---

## 12. Scaling Strategy

### 12.1 Horizontal Scaling

| Bottleneck               | Solution                                                                     |
| ------------------------ | ---------------------------------------------------------------------------- |
| High API request volume  | Add FastAPI instances behind Nginx upstream with `least_conn` load balancing |
| Slow Playwright captures | Increase `worker` service replicas in Docker Compose (`--replicas N`)        |
| LLM inference latency    | Provision additional Ollama Cloud capacity; enable model caching             |
| Redis saturation         | Upgrade to Redis Cluster mode; increase `maxmemory`                          |

### 12.2 Production Kubernetes Considerations

For production deployments at scale, migrate from Docker Compose to **Kubernetes** with:

- `Deployment` resources for FastAPI backend and Celery workers with auto-scaling (`HorizontalPodAutoscaler`).
- `StatefulSet` for Redis with persistent volume claims.
- `ConfigMap` + `Secret` for environment variable management.
- `Ingress` with nginx-ingress-controller for TLS termination and routing.
- `PersistentVolumeClaim` for screenshot asset storage (or replace with S3-compatible object storage).

---

## 13. Backup & Recovery

### 13.1 What to Back Up

| Data                      | Location                          | Backup Method                              |
| ------------------------- | --------------------------------- | ------------------------------------------ |
| Redis state data          | Docker volume `redis_data`        | `redis-cli BGSAVE` → copy `/data/dump.rdb` |
| Screenshot assets         | Docker volume `screenshot_assets` | rsync to S3/NFS                            |
| Export files              | Docker volume `export_files`      | rsync to S3/NFS                            |
| Application configuration | `.env` files                      | Vault / secret manager                     |

### 13.2 Backup Schedule

```bash
# Automated Redis backup (cron — daily at 02:00)
0 2 * * * docker exec redis redis-cli BGSAVE && \
  docker cp redis:/data/dump.rdb /backups/redis/dump_$(date +%Y%m%d).rdb

# Automated asset backup (cron — every 6 hours)
0 */6 * * * rsync -avz /var/lib/docker/volumes/screenshot_assets/_data/ \
  s3://docuagent-backups/assets/
```

---

## 14. Troubleshooting

### 14.1 Common Issues

| Issue                       | Symptom                                    | Resolution                                                                         |
| --------------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------- |
| Playwright browser crash    | Step capture errors, `--no-sandbox` errors | Add `--no-sandbox --disable-dev-shm-usage` to Chromium args; check system memory   |
| Redis connection refused    | `ConnectionRefusedError: [Errno 111]`      | Verify Redis container is running; check `REDIS_URL` in `.env`                     |
| Ollama API timeout          | `LLM_INFERENCE_TIMEOUT` errors             | Increase `OLLAMA_TIMEOUT_SECONDS`; check Ollama Cloud endpoint status              |
| SSE connection drops        | Progress bar stops; incomplete generation  | Verify Nginx `proxy_read_timeout` is ≥ 600s; check `proxy_buffering off`           |
| WeasyPrint PDF failure      | Export returns 500 error                   | Install WeasyPrint system dependencies: `apt install libpango-1.0-0 libharfbuzz0b` |
| Celery tasks not processing | Queue depth grows; no worker activity      | Restart Celery workers: `docker compose restart worker`                            |

### 14.2 Log Locations

```bash
# FastAPI logs
docker compose logs backend

# Celery worker logs
docker compose logs worker

# Nginx access/error logs
docker compose logs nginx

# Redis logs
docker compose logs redis

# Stream all service logs with timestamps
docker compose logs -f --timestamps
```

---

_← Previous: [Frontend Developer Guide](./06_frontend_developer_guide.md)_  
_→ Next: [Security & Data Privacy](./08_security_data_privacy.md)_

---

_Document ID: DOC-007 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite_
