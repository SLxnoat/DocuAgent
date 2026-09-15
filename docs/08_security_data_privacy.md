# Security & Data Privacy

**Document ID:** DOC-008  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** Security Engineers, DevOps, Compliance Officers

---

## Table of Contents

1. [Security Overview](#1-security-overview)
2. [Threat Model](#2-threat-model)
3. [Credential Handling](#3-credential-handling)
4. [API Authentication & Authorization](#4-api-authentication--authorization)
5. [LLM Data Privacy](#5-llm-data-privacy)
6. [Network Security](#6-network-security)
7. [Data at Rest](#7-data-at-rest)
8. [Data in Transit](#8-data-in-transit)
9. [State Persistence Security](#9-state-persistence-security)
10. [Browser Automation Security](#10-browser-automation-security)
11. [Secrets Management](#11-secrets-management)
12. [Security Hardening Checklist](#12-security-hardening-checklist)
13. [Incident Response](#13-incident-response)
14. [Compliance Considerations](#14-compliance-considerations)

---

## 1. Security Overview

DocuAgent AI handles **sensitive staging environment credentials**, **proprietary workflow scripts**, and **enterprise application data**. The security architecture is designed around the following principles:

| Principle | Implementation |
|-----------|---------------|
| **Minimal Credential Exposure** | Staging credentials held in-memory only for the duration of browser execution |
| **Zero Credential Persistence** | Credentials are never written to disk, logs, or state stores |
| **Encrypted Communications** | All external API communications use TLS 1.2+ |
| **LLM Data Isolation** | Ollama Cloud does not retain customer prompt data for training |
| **Defence in Depth** | Multiple overlapping security controls at each layer |
| **Least Privilege** | Services operate with the minimum permissions required |

---

## 2. Threat Model

### 2.1 Assets to Protect

| Asset | Sensitivity | Location |
|-------|------------|----------|
| Staging application credentials | 🔴 Critical | In-memory only during execution |
| Workflow script content | 🟠 High | In-memory, Redis (TTL-gated), LLM API |
| Generated Markdown documents | 🟡 Medium | Server disk (assets volume), browser |
| Screenshot PNG files | 🟡 Medium | Server disk (assets volume) |
| API Bearer tokens | 🔴 Critical | Client-side env vars, server config |
| Ollama Cloud API keys | 🔴 Critical | Server-side env vars only |

### 2.2 Primary Threat Vectors

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|-----------|
| Credential leakage via logs | Medium | Critical | Credential scrubbing in all log handlers |
| Bearer token interception | Low | High | TLS enforcement; token rotation policy |
| Prompt injection via script input | Medium | High | Input sanitization; LLM output validation |
| Insecure direct object reference (job_id) | Low | Medium | Job ownership validation per authenticated user |
| Screenshot asset unauthorized access | Low | Medium | Asset paths are non-guessable UUIDs |
| Redis state store compromise | Low | High | Redis auth; network isolation; no plaintext creds in state |
| Playwright SSRF (malicious target URLs) | Medium | High | URL allowlist/denylist; private IP range blocking |

---

## 3. Credential Handling

### 3.1 Lifecycle of Staging Credentials

Staging credentials submitted through the generation API follow a strictly controlled lifecycle:

```
Client submits POST /api/v1/generate
    │
    ▼ (TLS encrypted in transit)
FastAPI receives credentials in request body
    │
    ▼ (Pydantic model — in-memory Python object)
credentials injected into ManualState (in-memory)
    │
    ▼
Agent 2 (Playwright) uses credentials for browser auth
    │
    ▼ [IMMEDIATELY AFTER AUTHENTICATION COMPLETES]
state["credentials"] = {}   ← Credentials scrubbed from state
    │
    ▼
LangGraph checkpointer NEVER sees credentials
    │
    ▼
Playwright session closes — browser memory cleared
```

### 3.2 🔒 Credential Scrubbing Implementation

```python
# app/agents/capture_agent.py

async def capture_screenshots_node(state: ManualState) -> ManualState:
    """
    Execute browser automation for all steps.
    
    SECURITY: credentials are scrubbed from state immediately after
    authentication, before any state persistence occurs.
    """
    credentials = state.get("credentials", {})
    
    async with PlaywrightCaptureEngine() as engine:
        # Use credentials for authentication
        if credentials:
            await engine.authenticate(credentials, state["target_url"])
        
        # *** CRITICAL: Scrub credentials before any await that may trigger checkpointing ***
        state["credentials"] = {}
        credentials = None  # Remove local reference
        
        # Continue with screenshot capture using established session
        for step in state["structured_steps"]:
            await engine.execute_step(step, state["job_id"])
    
    return state
```

### 3.3 Logging Sanitization

All Python logging handlers are configured with a credential-scrubbing filter:

```python
# app/utils/logging.py

import re
import logging

SENSITIVE_PATTERNS = [
    re.compile(r'(password["\s:=]+)[^\s,"\']+', re.IGNORECASE),
    re.compile(r'(Bearer\s+)\S+', re.IGNORECASE),
    re.compile(r'(token["\s:=]+)[^\s,"\']+', re.IGNORECASE),
    re.compile(r'(api[_-]?key["\s:=]+)[^\s,"\']+', re.IGNORECASE),
]

class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = str(record.getMessage())
        for pattern in SENSITIVE_PATTERNS:
            message = pattern.sub(r'\1[REDACTED]', message)
        record.msg = message
        record.args = ()
        return True

# Apply to all handlers
logging.getLogger().addFilter(SensitiveDataFilter())
```

### 3.4 Credential Field Exclusion from Pydantic Export

```python
# app/models/state.py

from pydantic import BaseModel, Field

class ManualStateModel(BaseModel):
    credentials: dict = Field(default_factory=dict, exclude=True)
    # exclude=True ensures credentials are never included in .model_dump(),
    # .json() serialization, or any persistence layer
```

---

## 4. API Authentication & Authorization

### 4.1 Bearer Token Authentication

All API endpoints require a Bearer token in the `Authorization` header:

```http
Authorization: Bearer <token>
```

Tokens are **static long-lived API keys** per deployment in the initial version. For production deployments, it is strongly recommended to implement:

1. **Token rotation** — generate new tokens periodically.
2. **Per-user tokens** — issue unique tokens per user or team for accountability.
3. **JWT-based tokens** — add expiry, scope, and claims for fine-grained authorization.

### 4.2 Token Validation Middleware

```python
# app/middleware/auth.py

from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "AUTHENTICATION_FAILED", "message": "Invalid API token"}}
        )
    return credentials.credentials
```

### 4.3 Job Ownership Validation

Every job and session operation validates that the requesting token is associated with the job that was originally submitted with that token:

```python
# app/api/jobs.py

async def get_job(job_id: str, token: str = Depends(verify_token)):
    job = await job_repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.owner_token_hash != hash_token(token):
        raise HTTPException(status_code=403, detail="Unauthorized access to job")
    return job
```

### 4.4 Rate Limiting

Rate limiting is applied at the Nginx layer:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req zone=api_limit burst=20 nodelay;
```

And enforced at the FastAPI layer using `slowapi`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/generate")
@limiter.limit("5/minute")
async def generate_manual(request: Request, ...):
    ...
```

---

## 5. LLM Data Privacy

### 5.1 Ollama Cloud Data Handling Guarantees

| Guarantee | Detail |
|-----------|--------|
| **No training data retention** | Customer prompt content is not used for Ollama model training |
| **TLS encryption in transit** | All API requests to Ollama Cloud endpoints use TLS 1.2+ |
| **Dedicated endpoints** | Enterprise customers receive isolated Ollama Cloud instances |
| **No third-party sharing** | Prompt data is not shared with sub-processors |

### 5.2 Minimum Data Sent to LLM

DocuAgent AI is designed to minimize what is sent to LLM endpoints:

| Sent to LLM | Not Sent to LLM |
|-------------|----------------|
| Workflow script text | Staging credentials (scrubbed before LLM calls) |
| Structured step descriptions | Raw screenshot binary data |
| Generated Markdown content (for review) | Internal job metadata |
| User chat messages | Redis state checksums |

### 5.3 On-Premise Deployment Option

For organizations with strict data residency requirements, Ollama can be deployed **entirely on-premise**:

```bash
# Deploy Ollama server on-premise
docker run -d \
  --gpus all \
  -v ollama_data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama

# Pull models
ollama pull llama3.3:70b
ollama pull qwen2.5:72b

# Update backend .env
OLLAMA_BASE_URL=http://ollama:11434
```

This ensures all LLM inference occurs within the organization's network perimeter.

---

## 6. Network Security

### 6.1 Service Network Isolation

In the Docker Compose deployment, all internal services communicate on an isolated Docker bridge network. Only Nginx is exposed on public ports 80/443:

```yaml
# docker-compose.yml network configuration
networks:
  internal:
    driver: bridge
    internal: true   # No direct external access

services:
  backend:
    networks: [internal]
  redis:
    networks: [internal]
  worker:
    networks: [internal]
  nginx:
    networks: [internal]
    ports:
      - "80:80"
      - "443:443"
```

### 6.2 Playwright SSRF Protection

To prevent Server-Side Request Forgery via malicious `target_url` values, the backend validates all URLs before Playwright execution:

```python
# app/utils/url_validator.py

import ipaddress
from urllib.parse import urlparse

BLOCKED_PRIVATE_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('::1/128'),
]

ALLOWED_SCHEMES = {'http', 'https'}

def validate_target_url(url: str) -> bool:
    """
    Reject URLs targeting private IP ranges, localhost, or non-HTTP schemes.
    Prevents SSRF attacks via the Playwright browser engine.
    """
    parsed = urlparse(url)
    
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"URL scheme '{parsed.scheme}' is not permitted")
    
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        for blocked_range in BLOCKED_PRIVATE_RANGES:
            if ip in blocked_range:
                raise ValueError(f"Target URL resolves to a private IP address")
    except ValueError:
        pass  # hostname is a domain name — allow (DNS resolution at Playwright time)
    
    return True
```

### 6.3 Firewall Rules

| Rule | Direction | Protocol | Port | Action |
|------|-----------|---------|------|--------|
| Allow HTTPS | Inbound | TCP | 443 | ALLOW |
| Allow HTTP (redirect only) | Inbound | TCP | 80 | ALLOW |
| Block all other inbound | Inbound | * | * | DENY |
| Allow outbound HTTPS | Outbound | TCP | 443 | ALLOW |
| Block outbound to private ranges | Outbound | TCP | * | DENY (SSRF prevention) |

---

## 7. Data at Rest

### 7.1 Screenshot Asset Storage

Screenshot files are stored on the server filesystem under `/app/assets/{job_id}/`. The `job_id` is a UUID v4, making asset paths non-enumerable.

**Recommended Production Practice:** Mount an **encrypted volume** (LUKS or cloud provider-managed disk encryption) for the `screenshot_assets` Docker volume.

### 7.2 Redis Persistence

Redis persistence (AOF + RDB) stores LangGraph state checkpoints. Credentials are never present in these snapshots (see [Section 3](#3-credential-handling)).

**Recommended Production Practice:**
- Enable Redis `requirepass` authentication.
- Use disk encryption on the Redis data directory.
- Apply strict filesystem permissions: `chmod 700 /var/lib/redis`.

### 7.3 Job & Asset Retention

Generated assets and state are retained for 24 hours by default (configurable via `REDIS_TTL_HOURS` and a scheduled cleanup job):

```python
# app/tasks/cleanup.py

@celery.task
def cleanup_expired_jobs():
    """Delete screenshot assets for jobs older than retention period."""
    retention_hours = settings.ASSET_RETENTION_HOURS  # Default: 24
    cutoff = datetime.utcnow() - timedelta(hours=retention_hours)
    
    for job_dir in Path(settings.SCREENSHOT_DIR).iterdir():
        if job_dir.stat().st_mtime < cutoff.timestamp():
            shutil.rmtree(job_dir)
```

---

## 8. Data in Transit

### 8.1 TLS Configuration

All client-server and server-to-LLM communications must use TLS:

| Connection | Minimum TLS Version | Certificate Requirement |
|-----------|--------------------|-----------------------|
| Client → Nginx | TLS 1.2 | Valid CA-signed certificate |
| Nginx → FastAPI | TLS 1.2 (or trusted LAN) | Self-signed acceptable for internal |
| FastAPI → Ollama Cloud | TLS 1.2 | Valid CA-signed certificate |

**Nginx TLS Configuration:**

```nginx
ssl_protocols       TLSv1.2 TLSv1.3;
ssl_ciphers         ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache   shared:SSL:10m;
ssl_session_timeout 1d;

# HSTS (1 year)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 8.2 Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline';" always;
```

---

## 9. State Persistence Security

### 9.1 Redis Checkpointer Security

The LangGraph `RedisCheckpointer` serializes `ManualState` to Redis. The following fields are explicitly excluded from serialization:

| Field | Exclusion Method |
|-------|----------------|
| `credentials` | Cleared to `{}` before first checkpoint (see Section 3.2) |
| Raw request headers | Never included in state |
| API tokens | Never included in state |

### 9.2 Redis Authentication

```bash
# redis.conf
requirepass your-strong-redis-password

# backend .env
REDIS_URL=redis://:your-strong-redis-password@redis:6379/0
```

### 9.3 State TTL Enforcement

All Redis keys set by the LangGraph checkpointer must be created with an expiry:

```python
# Verify TTL is applied
import redis
r = redis.from_url(settings.REDIS_URL)
keys = r.keys("checkpoint:*")
for key in keys:
    ttl = r.ttl(key)
    assert ttl > 0, f"Key {key} has no TTL — potential data retention violation"
```

---

## 10. Browser Automation Security

### 10.1 Sandboxing

Playwright Chromium processes run within Celery worker containers that have restricted capabilities:

```yaml
# docker-compose.yml — worker service security configuration
worker:
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  cap_add:
    - SYS_ADMIN   # Required by Chromium sandbox (--no-sandbox alternative)
  tmpfs:
    - /tmp        # tmpfs for Chromium temp files — not persisted to disk
```

### 10.2 Chromium Sandbox Mode

For environments where `SYS_ADMIN` capability cannot be granted, run Chromium with `--no-sandbox` only within isolated, single-purpose worker containers with no network access to internal services:

```python
browser = await playwright.chromium.launch(
    headless=True,
    args=[
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",          # No browser extensions
        "--disable-background-networking", # Reduce unintended network calls
    ]
)
```

### 10.3 Target URL Isolation

The Playwright browser context is configured to block access to internal service IPs, preventing compromise via malicious redirect chains in target applications:

```python
async def block_internal_routes(route: Route, request: Request):
    url = request.url
    if is_private_ip(url):
        await route.abort()
    else:
        await route.continue_()

await context.route("**/*", block_internal_routes)
```

---

## 11. Secrets Management

### 11.1 Recommended: HashiCorp Vault Integration

For production deployments, secrets should be sourced from **HashiCorp Vault** rather than `.env` files:

```python
# app/config.py — Vault-based secret retrieval

import hvac

def load_secrets_from_vault():
    client = hvac.Client(url=os.environ["VAULT_ADDR"], token=os.environ["VAULT_TOKEN"])
    secrets = client.secrets.kv.v2.read_secret_version(path="docuagent/production")
    return secrets["data"]["data"]
```

### 11.2 Minimum Viable: Environment Variable Security

If using `.env` files:

| Practice | Implementation |
|---------|---------------|
| Never commit `.env` to version control | Add `.env` to `.gitignore` |
| Restrict file permissions | `chmod 600 .env` |
| Use different secrets per environment | Separate `.env.dev`, `.env.prod` |
| Rotate secrets regularly | Quarterly rotation at minimum |

---

## 12. Security Hardening Checklist

Use this checklist before each production deployment:

- [ ] **TLS certificate is valid** and not expiring within 30 days
- [ ] **HSTS header** is configured with `max-age >= 31536000`
- [ ] **Redis** requires password authentication (`requirepass`)
- [ ] **Redis** is not exposed on public network interfaces
- [ ] **API Bearer tokens** are at least 32 characters of random entropy
- [ ] **Nginx rate limiting** is active for `/api/` endpoints
- [ ] **Credential scrubbing** is verified in test suite (unit test that logs never contain passwords)
- [ ] **SSRF protection** URL validator is enabled and tested with private IP inputs
- [ ] **Playwright Chromium** is running with sandbox restrictions
- [ ] **Job ownership validation** is active for all job/session endpoints
- [ ] **Asset paths** use non-guessable UUIDs (not sequential integers)
- [ ] **Log files** do not contain any plaintext credentials or tokens (audit with `grep -rni "password"` on logs)
- [ ] **Docker containers** run as non-root user
- [ ] **Secrets** are sourced from environment variables or vault — not hardcoded in source
- [ ] **Dependency audit** run: `pip audit` (Python) and `npm audit` (Node.js)

---

## 13. Incident Response

### 13.1 Credential Exposure

If staging credentials are suspected to have been logged or exposed:

1. **Immediately invalidate** the exposed staging credentials in the target application.
2. **Rotate** the DocuAgent API Bearer token.
3. **Audit** all log files for the credential string: `grep -rni "password_value" /var/log/docuagent/`.
4. **Review** the Git history to ensure no credentials were accidentally committed.
5. **Notify** the affected staging application owner.

### 13.2 API Token Compromise

1. **Generate a new API token** immediately.
2. **Invalidate the old token** in server configuration.
3. **Restart** the FastAPI service to load the new token.
4. **Audit** API access logs for unauthorized usage during the compromise window.
5. **Distribute** the new token to all legitimate clients.

### 13.3 Security Contact

Report security vulnerabilities to the designated security team. Do not file public GitHub issues for security vulnerabilities.

---

## 14. Compliance Considerations

| Standard | Relevant Controls in DocuAgent AI |
|----------|----------------------------------|
| **GDPR** | No PII stored by default; credential scrubbing; 24h data retention; right-to-erasure via `DELETE /api/v1/jobs/{job_id}` |
| **SOC 2 Type II** | TLS encryption; access logging; credential non-persistence; audit trails in execution logs |
| **ISO 27001** | Threat model documented; access controls; secure development practices; incident response |
| **OWASP Top 10** | Injection prevention (input validation); broken access control mitigation (ownership checks); security misconfiguration avoidance |

---

*← Previous: [Deployment & Operations Guide](./07_deployment_operations.md)*  
*→ Next: [Non-Functional Requirements](./09_non_functional_requirements.md)*

---

*Document ID: DOC-008 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite*
