import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    // 100 concurrent health checks verifying p95 <= 200ms
    health_stress_test: {
      executor: "constant-vus",
      vus: 100,
      duration: "30s",
      exec: "healthCheck",
    },
    // 5 concurrent generation workflows completed within 5 minutes
    generation_load_test: {
      executor: "per-vu-iterations",
      vus: 5,
      iterations: 1,
      maxDuration: "5m",
      exec: "generationWorkflow",
      startTime: "35s",
    },
  },
  thresholds: {
    "http_req_duration{scenario:health_stress_test}": ["p(95)<200"], // p95 <= 200ms
    http_req_failed: ["rate<0.01"], // less than 1% failure
  },
};

const BASE_URL = __ENV.API_URL || "http://localhost:8000";
const API_TOKEN = __ENV.API_TOKEN || "dev-token-change-in-production";

export function healthCheck() {
  const res = http.get(`${BASE_URL}/health`);
  check(res, {
    "status is 200": (r) => r.status === 200,
    "healthy status": (r) => JSON.parse(r.body).status === "healthy",
  });
  sleep(0.1);
}

export function generationWorkflow() {
  const payload = JSON.stringify({
    target_url: "https://demo-app.example.com",
    raw_script: `
      1. Open application dashboard
      2. Click on user profile menu
      3. Navigate to settings section
      4. Toggle email notifications preference
      5. Select timezone dropdown
      6. Choose UTC from list
      7. Enter secondary recovery email
      8. Click save changes button
      9. Confirm success notification
      10. Log out of session
    `,
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_TOKEN}`,
    },
  };

  const res = http.post(`${BASE_URL}/api/v1/generate`, payload, params);
  check(res, {
    "generation accepted": (r) => r.status === 200 || r.status === 202,
  });

  if (res.status === 200 || res.status === 202) {
    const data = JSON.parse(res.body);
    const jobId = data.job_id;

    // Poll status until completion or timeout
    let completed = false;
    for (let i = 0; i < 30; i++) {
      sleep(2);
      const statusRes = http.get(
        `${BASE_URL}/api/v1/jobs/${jobId}/status`,
        params,
      );
      if (statusRes.status === 200) {
        const statusData = JSON.parse(statusRes.body);
        if (
          statusData.status === "completed" ||
          statusData.status === "awaiting_input"
        ) {
          completed = true;
          break;
        }
      }
    }
    check(completed, { "workflow finished within SLA": (c) => c === true });
  }
}
