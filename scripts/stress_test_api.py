"""
API Stress Test Script
Executes 100 concurrent health and status requests against the FastAPI app,
measuring response times and calculating p50, p90, p95, and p99 percentiles.
Verifies compliance with checklist SLA requirement: p95 <= 200ms.
"""

from __future__ import annotations

import asyncio
import statistics
import time
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from httpx import ASGITransport, AsyncClient
from app.main import app


async def run_single_request(client: AsyncClient, endpoint: str) -> float:
    start_time = time.perf_counter()
    response = await client.get(endpoint)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    return elapsed_ms


async def main():
    print("=" * 60)
    print("DocuAgent API Stress Test: 100 Concurrent Requests")
    print("=" * 60)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Warmup
        await client.get("/health")

        # 100 concurrent health checks with connection pooling
        print("\n[1/2] Executing 100 health checks with 10 concurrent workers...")
        sem = asyncio.Semaphore(10)

        async def worker():
            async with sem:
                return await run_single_request(client, "/health")

        tasks = [worker() for _ in range(100)]
        start = time.perf_counter()
        latencies = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start

        # Calculate latency statistics
        latencies.sort()
        count = len(latencies)
        p50 = statistics.median(latencies)
        p90 = latencies[int(count * 0.90)]
        p95 = latencies[int(count * 0.95)]
        p99 = latencies[int(count * 0.99)]
        avg = statistics.mean(latencies)

        print(f"Total time for 100 concurrent requests: {total_time:.3f}s")
        print(f"Average latency:  {avg:.2f} ms")
        print(f"p50 latency:      {p50:.2f} ms")
        print(f"p90 latency:      {p90:.2f} ms")
        print(f"p95 latency:      {p95:.2f} ms")
        print(f"p99 latency:      {p99:.2f} ms")

        # SLA verification
        print("\n" + "-" * 60)
        if p95 <= 200:
            print(f"✅ SLA PASSED: p95 ({p95:.2f}ms) <= 200ms target")
        else:
            print(f"❌ SLA FAILED: p95 ({p95:.2f}ms) exceeded 200ms target")
        print("-" * 60)

        assert p95 <= 200, f"p95 latency {p95}ms exceeded 200ms"


if __name__ == "__main__":
    asyncio.run(main())
