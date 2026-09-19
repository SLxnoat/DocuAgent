# DocuAgent AI — Production System Runbook

**Document ID:** RUNBOOK-001  
**Version:** 1.0.0  
**Target Environment:** Production / Staging  
**Service Tier:** Mission-Critical AI Documentation Engine

---

## 1. System Architecture Overview

```
                          [ Client Browser ]
                                   │
                                   ▼
                       [ Nginx Reverse Proxy: 80/443 ]
                   ┌───────────────┴───────────────┐
                   ▼                               ▼
      [ Frontend SPA (Nginx) ]         [ Backend API (FastAPI) ]
                                                   │
                   ┌───────────────────────────────┴───────────────────────────────┐
                   ▼                               ▼                               ▼
       [ Redis 7 (Broker/PubSub) ]    [ Celery Distributed Workers ]    [ Ollama Local Inference ]
                   │                               │
                   ▼                               ▼
           [ Redis RDB Volume ]       [ Shared Assets / Exports Vol ]
```

---

## 2. Service Management & Recovery

### 2.1 Starting the Stack

```bash
# Production stack start in detached mode
docker compose up -d

# Check all containers health status
docker compose ps
```

### 2.2 Graceful Service Restart

```bash
# Restart single component without dropping traffic
docker compose restart backend
docker compose restart worker
docker compose restart nginx

# Full stack rolling restart
docker compose down && docker compose up -d
```

### 2.3 Emergency Recovery & Hard Reset

```bash
# In case of worker deadlock or browser process leaks
docker compose kill worker backend
docker compose rm -f worker backend
docker compose up -d --build worker backend
```

---

## 3. Log Inspection & Diagnostics

### 3.1 Real-Time Container Logs

```bash
# Follow unified logs across all services
docker compose logs -f --tail=100

# Inspect specific service logs
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f nginx
docker compose logs -f redis
```

### 3.2 Error Log Filtering

```bash
# Filter errors in worker execution
docker compose logs worker | grep -E "ERROR|CRITICAL|Traceback"

# Inspect Nginx upstream connection errors
docker compose logs nginx | grep -E "502|504|upstream"
```

---

## 4. Observability & Monitoring Dashboards

| Service                | Endpoint / URL             | Purpose                                                    |
| ---------------------- | -------------------------- | ---------------------------------------------------------- |
| **Health Check**       | `http://localhost/health`  | System liveness, version, and uptime check                 |
| **Prometheus Metrics** | `http://localhost/metrics` | Request latency, status code counts, throughput            |
| **Celery Flower**      | `http://localhost:5555`    | Real-time task queue depth, worker states, and retry count |
| **Frontend UI**        | `http://localhost/`        | End-user interactive manual generator & Monaco editor      |

---

## 5. Credential Rotation Procedures

### 5.1 API Bearer Token Rotation

1. Generate high-entropy 256-bit token:
   ```bash
   openssl rand -hex 32
   ```
2. Update `.env` or deployment secrets:
   ```env
   API_TOKEN=<new-generated-token>
   ```
3. Restart backend service gracefully:
   ```bash
   docker compose up -d --no-deps backend
   ```

### 5.2 Redis Access Password Rotation

1. Update `REDIS_URL`, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND` in `.env`.
2. Update Redis configuration and restart:
   ```bash
   docker compose restart redis backend worker flower
   ```

---

## 6. Incident Playbook & Troubleshooting

### Scenario A: Playwright Browser Timeout on Target App

- **Symptom:** Worker log displays `TimeoutError: Element <selector> not found`.
- **Cause:** Slow remote application rendering or dynamic single-page DOM hydration delay.
- **Resolution:** The pipeline automatically records a fallback full-page screenshot without element highlighting. If the page completely fails to respond, adjust `PLAYWRIGHT_NAVIGATION_TIMEOUT_MS=60000` in `.env`.

### Scenario B: Ollama LLM Unresponsive or 503

- **Symptom:** `Draft compilation timed out` or `Analyzer agent failed`.
- **Resolution:**
  1. Check Ollama host: `curl http://localhost:11434/api/tags`
  2. Verify required models are loaded (`deepseek-r1:14b` or fallback `mistral`).
  3. Ensure GPU memory allocation is sufficient.

### Scenario C: PDF Export Failure (WeasyPrint / Pandoc)

- **Symptom:** `Export generation failed for format pdf`.
- **Resolution:**
  1. Verify WeasyPrint dependencies (`libpango-1.0-0`, `libcairo2`).
  2. Verify pinned version: `pydyf==0.11.0` (pydyf 0.12+ breaks WeasyPrint 62.3).
  3. Inspect Pandoc markdown input formatting.

### Scenario D: Redis Disk Full

- **Symptom:** `MISCONF Redis is configured to save RDB snapshots, but is currently not able to persist on disk`.
- **Resolution:**
  1. Trigger manual backup cleanup:
     ```bash
     bash scripts/backup_redis.sh
     ```
  2. Verify disk usage on host: `df -h /var/lib/docker/volumes`
  3. Purge expired keys: `redis-cli bgsave`

---

## 7. Automated Backups & Disaster Recovery

- **Scheduled Backup:** Automated via `scripts/backup_redis.sh` at `02:00 UTC` daily.
- **Backup Location:** `/var/backups/docuagent/redis/dump_<timestamp>.rdb.gz`
- **Restoration Step:**
  ```bash
  gunzip -c dump_<timestamp>.rdb.gz > dump.rdb
  docker cp dump.rdb docuagent-redis:/data/dump.rdb
  docker compose restart redis
  ```
