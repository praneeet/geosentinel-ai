"""
GeoSentinel AI - Production Concurrency & Load Benchmark
Simulates up to 100 concurrent analytical users executing REST API queries,
database transactions, and WebSocket alert dispatching.
Calculates Requests Per Second (RPS), Mean, p95, and p99 latencies, and error rates.
AKGEC Department of IT | CSIT Group 32
"""
import os
import sys
import time
import json
import asyncio
import numpy as np
from typing import List, Dict, Any

base_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(base_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, os.path.join(project_root, "backend"))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings

ENDPOINTS = [
    ("/api/health", "GET"),
    ("/api/countries", "GET"),
    ("/api/risk/map", "GET"),
    ("/api/trends?days=30", "GET"),
    ("/api/alerts?limit=20", "GET"),
    ("/api/articles?page=1&page_size=15", "GET"),
    ("/api/events?page=1&page_size=15", "GET"),
    ("/api/countries/UKR/risk", "GET"),
    ("/api/countries/UKR/forecast?days=7", "GET"),
    ("/api/countries/UKR/history?days=30", "GET"),
    ("/api/countries/UKR/summary", "GET"),
]

async def run_single_user_session(client: AsyncClient, num_requests: int) -> List[Dict[str, Any]]:
    results = []
    for _ in range(num_requests):
        path, method = ENDPOINTS[np.random.randint(0, len(ENDPOINTS))]
        t0 = time.perf_counter()
        status_code = 0
        error = None
        try:
            if method == "GET":
                resp = await client.get(path, timeout=10.0)
                status_code = resp.status_code
        except Exception as e:
            error = str(e)
        duration_ms = (time.perf_counter() - t0) * 1000.0
        results.append({
            "path": path,
            "status": status_code,
            "duration_ms": duration_ms,
            "error": error,
        })
    return results

async def execute_concurrency_test(concurrent_users: int = 100, requests_per_user: int = 5) -> Dict[str, Any]:
    print(f"\n================================================================================")
    print(f" Starting Concurrency Load Test: {concurrent_users} Concurrent Users ({concurrent_users * requests_per_user} Total Requests)")
    print(f"================================================================================")

    transport = ASGITransport(app=app)
    t_start = time.perf_counter()

    async with AsyncClient(transport=transport, base_url="http://benchmark") as client:
        tasks = [
            run_single_user_session(client, requests_per_user)
            for _ in range(concurrent_users)
        ]
        user_results = await asyncio.gather(*tasks)

    total_duration = time.perf_counter() - t_start
    all_requests = [req for u in user_results for req in u]
    total_reqs = len(all_requests)

    latencies = [r["duration_ms"] for r in all_requests]
    errors = [r for r in all_requests if r["status"] != 200 or r["error"] is not None]
    error_rate = (len(errors) / total_reqs) * 100.0 if total_reqs > 0 else 0.0
    rps = total_reqs / total_duration if total_duration > 0 else 0.0

    mean_lat = float(np.mean(latencies))
    median_lat = float(np.median(latencies))
    p95_lat = float(np.percentile(latencies, 95))
    p99_lat = float(np.percentile(latencies, 99))
    min_lat = float(np.min(latencies))
    max_lat = float(np.max(latencies))

    print(f"\nExecution Summary:")
    print(f"  • Total Requests Completed : {total_reqs}")
    print(f"  • Total Wall Time          : {total_duration:.2f} s")
    print(f"  • Throughput               : {rps:.1f} Requests / sec")
    print(f"  • Mean Latency             : {mean_lat:.2f} ms")
    print(f"  • Median (p50) Latency     : {median_lat:.2f} ms")
    print(f"  • 95th Percentile (p95)    : {p95_lat:.2f} ms")
    print(f"  • 99th Percentile (p99)    : {p99_lat:.2f} ms")
    print(f"  • Min / Max Latency        : {min_lat:.2f} ms / {max_lat:.2f} ms")
    print(f"  • Error Rate               : {error_rate:.2f}% ({len(errors)} failed)")

    return {
        "concurrent_users": concurrent_users,
        "total_requests": total_reqs,
        "duration_seconds": round(total_duration, 2),
        "requests_per_second": round(rps, 1),
        "mean_latency_ms": round(mean_lat, 2),
        "p95_latency_ms": round(p95_lat, 2),
        "p99_latency_ms": round(p99_lat, 2),
        "error_rate_pct": round(error_rate, 2),
    }

if __name__ == "__main__":
    from app.database.session import init_db
    async def main():
        await init_db()
        # Controlled warmup: 20 users
        await execute_concurrency_test(concurrent_users=20, requests_per_user=5)
        # Full capacity load: 100 concurrent simulated users
        summary = await execute_concurrency_test(concurrent_users=100, requests_per_user=5)
        print("\nFinal Benchmark Metric Payload:")
        print(json.dumps(summary, indent=2))
    asyncio.run(main())
