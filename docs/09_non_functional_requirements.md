# Non-Functional Requirements

**Document ID:** DOC-009  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** System Architects, DevOps Engineers, QA Engineers

---

## Table of Contents

1. [Overview](#1-overview)
2. [Performance Requirements](#2-performance-requirements)
3. [Scalability Requirements](#3-scalability-requirements)
4. [Reliability & Availability Requirements](#4-reliability--availability-requirements)
5. [Fault Tolerance & Graceful Degradation](#5-fault-tolerance--graceful-degradation)
6. [Security Requirements](#6-security-requirements)
7. [Usability Requirements](#7-usability-requirements)
8. [Maintainability Requirements](#8-maintainability-requirements)
9. [Observability Requirements](#9-observability-requirements)
10. [Compliance Requirements](#10-compliance-requirements)
11. [NFR Verification Matrix](#11-nfr-verification-matrix)

---

## 1. Overview

Non-Functional Requirements (NFRs) define the operational quality attributes that DocuAgent AI must meet beyond its functional capabilities. These requirements govern how the system performs, scales, fails, and is maintained. All NFRs are written as verifiable, measurable targets.

### 1.1 NFR Priority Classification

| Priority | Label | Description |
|----------|-------|-------------|
| **P0** | Must Have | System cannot be released without meeting this requirement |
| **P1** | Should Have | High-priority; deviation requires documented exception |
| **P2** | Nice to Have | Desirable; addressed when capacity allows |

---

## 2. Performance Requirements

### 2.1 End-to-End Generation Latency

| Metric | Target | Priority |
|--------|--------|----------|
| Full manual generation (10-step workflow) | ≤ 3 minutes | P0 |
| Full manual generation (25-step workflow) | ≤ 7 minutes | P0 |
| Full manual generation (50-step workflow) | ≤ 12 minutes | P1 |
| Script analysis phase (Agent 1) | ≤ 15 seconds | P0 |
| Per-step screenshot capture | ≤ 12 seconds/step | P0 |
| Markdown compilation (Agent 3) | ≤ 30 seconds | P0 |
| Quality review phase (Agent 4) | ≤ 20 seconds | P1 |

> 📌 **Baseline Context:** Traditional manual documentation of a 20-step workflow requires 4–8 hours. A 3-minute automated generation represents a **99%+ time reduction**.

### 2.2 Chat Refinement Latency

| Metric | Target | Priority |
|--------|--------|----------|
| Text-only edit response time | ≤ 10 seconds | P0 |
| Structural edit response time | ≤ 15 seconds | P1 |
| Single-step re-capture response time | ≤ 20 seconds | P1 |
| Time to first token (chat streaming) | ≤ 2 seconds | P1 |

### 2.3 Frontend Performance

| Metric | Target | Priority |
|--------|--------|----------|
| Initial page load (LCP) | ≤ 2.5 seconds | P0 |
| Time to Interactive (TTI) | ≤ 3.5 seconds | P0 |
| Editor keystroke response latency | ≤ 16ms (60 fps) | P0 |
| Markdown preview re-render latency | ≤ 100ms after edit | P1 |
| First SSE event received after job submit | ≤ 2 seconds | P0 |

### 2.4 API Response Times (Synchronous Endpoints)

| Endpoint | Target (p95) | Priority |
|----------|-------------|----------|
| `POST /api/v1/generate` (acceptance) | ≤ 500ms | P0 |
| `GET /api/v1/jobs/{job_id}` | ≤ 200ms | P0 |
| `POST /api/v1/chat/{session_id}` | ≤ 10 seconds (full response) | P0 |
| `GET /api/v1/export/{job_id}` (Markdown) | ≤ 500ms | P0 |
| `GET /api/v1/export/{job_id}` (PDF) | ≤ 15 seconds | P1 |

---

## 3. Scalability Requirements

### 3.1 Concurrency Targets

| Metric | Target | Priority |
|--------|--------|----------|
| Concurrent active generation jobs | ≥ 5 (single server) | P0 |
| Concurrent active generation jobs | ≥ 50 (scaled cluster) | P1 |
| Concurrent active chat sessions | ≥ 100 | P0 |
| Concurrent SSE stream connections | ≥ 200 | P0 |
| Concurrent WebSocket connections | ≥ 100 | P1 |

### 3.2 Throughput Targets

| Metric | Target | Priority |
|--------|--------|----------|
| Completed manuals per hour (single server) | ≥ 10 | P0 |
| Completed manuals per hour (scaled cluster) | ≥ 100 | P1 |
| Chat refinement requests per minute (global) | ≥ 60 | P0 |

### 3.3 Horizontal Scaling Characteristics

The system must support **linear horizontal scaling** of the following components without architectural changes:

| Component | Scaling Method | Scaling Unit |
|-----------|---------------|-------------|
| FastAPI Backend | Add Gunicorn workers or replica containers | Per vCPU |
| Celery Workers | Increase `--concurrency` or add worker replicas | Per Playwright instance |
| Redis | Upgrade instance size (vertical) or Redis Cluster (horizontal) | Per memory requirement |
| Nginx | Add upstream backend instances | Per active connection |

### 3.4 Data Volume Targets

| Metric | Target |
|--------|--------|
| Max screenshot assets per job | 50 files |
| Max single screenshot file size | 2 MB (PNG) |
| Max total asset storage per job | 100 MB |
| Max generated Markdown size | 500 KB |
| Max generated PDF size | 50 MB |

---

## 4. Reliability & Availability Requirements

### 4.1 Availability Targets

| Environment | Target Availability | Max Downtime/Month |
|-------------|--------------------|--------------------|
| Production | 99.5% uptime | ≤ 3.6 hours |
| Staging | 95% uptime | ≤ 36 hours |

### 4.2 Mean Time Between Failures (MTBF)

| Component | Target MTBF |
|-----------|------------|
| FastAPI Backend | ≥ 30 days between unplanned restarts |
| Celery Workers | ≥ 7 days (Playwright workers may need periodic recycling) |
| Redis | ≥ 90 days between failures (managed service target) |

### 4.3 Mean Time to Recovery (MTTR)

| Failure Scenario | Target MTTR |
|-----------------|------------|
| Single Celery worker crash | ≤ 30 seconds (Docker auto-restart) |
| FastAPI process crash | ≤ 60 seconds (Gunicorn worker respawn) |
| Full service restart | ≤ 5 minutes |
| Redis failover (replica promotion) | ≤ 2 minutes |

### 4.4 Job Completion Rate

| Metric | Target | Priority |
|--------|--------|----------|
| Overall job success rate | ≥ 95% | P0 |
| Jobs completing with at least 80% of steps captured | ≥ 99% | P0 |
| Jobs failing with zero output | ≤ 1% | P0 |

---

## 5. Fault Tolerance & Graceful Degradation

### 5.1 Required Failure Modes

The following failure modes **must** be handled gracefully without crashing the pipeline:

| Failure | Graceful Behavior |
|---------|------------------|
| Playwright selector not found | Log to `error_states`; take fallback viewport screenshot; continue pipeline |
| Playwright navigation timeout | Log warning; insert `[Insert Screenshot Here]` placeholder; continue pipeline |
| LLM API timeout (single call) | Retry up to 3 times with exponential backoff |
| LLM API permanent failure | Fail job gracefully; return partial output with error notification |
| Quality review fails 3 times | Force-approve and present document with quality warning banner |
| Export generation fails (PDF) | Fall back to returning Markdown; log export error |
| Redis connection lost mid-job | Celery worker retries with `autoretry_for=(ConnectionError,)` |
| Anti-bot detection blocks Playwright | Insert `[Insert Screenshot Here]` placeholders for all remaining steps; generate text-only manual |

### 5.2 Text-Only Fallback Mode

When browser automation is completely blocked (e.g., CAPTCHA-protected application), the system must still produce a complete, useful document:

```
[Insert Screenshot Here: Step 1 — Navigate to https://app.example.com/login]

[Insert Screenshot Here: Step 2 — Enter credentials and click Login]

[Insert Screenshot Here: Step 3 — Click 'Users' in the left sidebar]
```

The placeholders are clearly formatted for a technical writer to replace with manually captured screenshots post-generation.

### 5.3 Partial Output Delivery

If a job is interrupted after the screenshot capture phase but before Markdown compilation completes, the frontend must offer the user the option to:
- Download the raw structured steps JSON for manual documentation.
- Resume the pipeline from the interrupted stage (not available in v1; roadmap item).

---

## 6. Security Requirements

> 📌 See [Security & Data Privacy](./08_security_data_privacy.md) for full security specifications. This section summarizes NFR-level requirements only.

| Requirement | Target | Priority |
|-------------|--------|----------|
| Staging credentials persistence duration | Zero — in-memory only | P0 |
| Credential appearance in logs | Zero occurrences | P0 |
| API communications encrypted | 100% via TLS 1.2+ | P0 |
| API rate limiting | Active on all endpoints | P0 |
| Job ownership enforcement | 100% of job/session access | P0 |
| Asset path guessability | UUID v4 — non-enumerable | P1 |
| SSRF protection active | All `target_url` inputs validated | P0 |
| Dependency vulnerability scan | Before every production deployment | P1 |

---

## 7. Usability Requirements

### 7.1 User Experience

| Requirement | Target | Priority |
|-------------|--------|----------|
| Time for a non-technical user to submit a generation job | ≤ 3 minutes | P0 |
| Real-time progress visibility | SSE progress updates ≤ 2 seconds latency | P0 |
| Error messages | Human-readable; include suggested remediation | P1 |
| Mobile viewport responsiveness | Layout usable on ≥ 768px viewport width | P2 |
| Dark mode support | Supported via Tailwind dark class | P1 |
| Accessibility | WCAG 2.1 Level AA compliance for core user flows | P1 |

### 7.2 Documentation Completeness

| Requirement | Target |
|-------------|--------|
| Prerequisites section always present | 100% of generated manuals |
| Step count accuracy (all steps from script represented) | 100% |
| Screenshot coverage (captured or fallback placeholder) | 100% of steps |
| Troubleshooting section for failed captures | 100% of steps with `error_states` entries |

---

## 8. Maintainability Requirements

### 8.1 Code Quality

| Metric | Target | Priority |
|--------|--------|----------|
| Backend test coverage | ≥ 80% (unit + integration) | P1 |
| Frontend test coverage | ≥ 70% (unit + component) | P1 |
| Linting standards | No errors (flake8/ruff for Python; ESLint for TypeScript) | P0 |
| Static type checking | mypy for Python (strict mode); TypeScript strict mode | P1 |

### 8.2 Dependency Management

| Requirement | Target |
|-------------|--------|
| Python dependency audit | `pip audit` run on every CI build |
| Node.js dependency audit | `npm audit` run on every CI build |
| Dependency update cadence | Security patches within 48 hours; minor versions monthly |
| Dependency pinning | All dependencies pinned with `requirements.txt` / `package-lock.json` |

### 8.3 Documentation Maintenance

| Requirement | Target |
|-------------|--------|
| API documentation accuracy | API Reference must reflect actual endpoint behavior within 1 sprint |
| Architecture diagram currency | Updated within 1 sprint of any architectural change |
| Runbook completeness | Runbooks exist for all P0 operational failure scenarios |

### 8.4 Deployment Automation

| Requirement | Target | Priority |
|-------------|--------|----------|
| CI/CD pipeline | Automated build, test, and deploy on main branch push | P0 |
| Rollback capability | Single command rollback to previous deployment | P0 |
| Zero-downtime deployments | Blue-green or rolling update strategy | P1 |
| Environment promotion | Staging environment mirrors production configuration | P1 |

---

## 9. Observability Requirements

### 9.1 Logging

| Requirement | Target | Priority |
|-------------|--------|----------|
| Structured log format | JSON format for all service logs | P0 |
| Log levels implemented | ERROR, WARNING, INFO, DEBUG (configurable) | P0 |
| Request ID propagation | Unique `X-Request-ID` traced across all services | P1 |
| Log retention | ≥ 30 days for production logs | P1 |
| Sensitive data in logs | Zero credential or token occurrences | P0 |

### 9.2 Metrics

| Metric | Tooling | Priority |
|--------|---------|----------|
| HTTP request rate, latency, error rate | Prometheus + FastAPI instrumentator | P0 |
| Celery task success/failure rate | Celery Flower + Prometheus | P0 |
| Active SSE/WebSocket connections | Custom Prometheus gauge | P1 |
| Ollama API call latency | Custom Prometheus histogram | P1 |
| Screenshot capture success/fallback ratio | Custom Prometheus counter | P1 |
| Redis memory usage | Redis Exporter for Prometheus | P1 |

### 9.3 Distributed Tracing

| Requirement | Target | Priority |
|-------------|--------|----------|
| Trace propagation | OpenTelemetry trace context across FastAPI + Celery | P2 |
| Trace backend | Jaeger or Tempo | P2 |

### 9.4 Alerting

| Alert | Condition | Severity |
|-------|-----------|---------|
| API error rate spike | Error rate > 5% over 5 minutes | 🔴 Critical |
| Job failure rate high | Failure rate > 10% over 15 minutes | 🔴 Critical |
| Ollama API degraded | Timeout rate > 5% over 5 minutes | 🟠 High |
| Celery queue depth | > 20 pending tasks for > 5 minutes | 🟠 High |
| Redis memory high | > 80% of maxmemory | 🟡 Warning |
| SSL certificate expiry | < 30 days until expiry | 🟡 Warning |
| Disk usage high | > 80% of screenshot asset volume | 🟡 Warning |

---

## 10. Compliance Requirements

| Requirement | Standard | Priority |
|-------------|---------|----------|
| Data retention ≤ 24 hours by default | GDPR Article 5 | P0 |
| Right to erasure via job deletion API | GDPR Article 17 | P0 |
| All API communications encrypted | PCI-DSS Requirement 4, SOC 2 CC6 | P0 |
| Access to assets restricted to job owner | SOC 2 CC6 | P0 |
| Security incident detection capability | SOC 2 CC7 | P1 |
| Audit log retention ≥ 90 days | SOC 2 CC7 | P1 |

---

## 11. NFR Verification Matrix

This matrix defines how each NFR category is verified:

| NFR Category | Verification Method | Frequency |
|-------------|--------------------|-----------| 
| **Performance** | Load testing with k6 or Locust (simulated 10, 25, 50-step workflows) | Before each major release |
| **Scalability** | Concurrent load test (5, 10, 50 simultaneous jobs) | Before each major release |
| **Reliability** | Chaos engineering (kill individual services; verify auto-recovery) | Quarterly |
| **Fault Tolerance** | Failure injection testing (mock Playwright failures, LLM timeouts) | On each CI run |
| **Security** | DAST scan (OWASP ZAP); dependency audit; manual penetration test | Before each major release |
| **Usability** | Usability testing session with 3+ non-technical users | Before each major release |
| **Maintainability** | Code coverage report; linting CI gate; dependency audit | On every CI run |
| **Observability** | Alert firing test (manually trigger threshold conditions) | Monthly |
| **Compliance** | GDPR data flow audit; credential log scan | Quarterly |

### 11.1 Performance Test Baseline Commands

```bash
# Load test: 10 concurrent job submissions over 5 minutes
k6 run --vus 10 --duration 5m scripts/k6_generate_job.js

# API stress test: 100 concurrent /health + /jobs poll requests
k6 run --vus 100 --duration 2m scripts/k6_api_stress.js

# Chat latency test: 20 concurrent chat sessions
k6 run --vus 20 --duration 3m scripts/k6_chat_latency.js
```

---

*← Previous: [Security & Data Privacy](./08_security_data_privacy.md)*  
*→ Next: [Future Roadmap](./10_future_roadmap.md)*

---

*Document ID: DOC-009 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite*
