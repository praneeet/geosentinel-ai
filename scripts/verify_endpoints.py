import urllib.request
import json


def verify_all_endpoints(base_url="http://127.0.0.1:8000"):
    print("=" * 70)
    print("GeoSentinel AI — Core Endpoint Verification")
    print(f"Target Base URL: {base_url}")
    print("=" * 70)

    get_endpoints = [
        ("/api/health", "System Health Probe"),
        ("/api/countries", "Countries & Risk Indices"),
        ("/api/countries/UKR/risk", "Country Risk Score Detail (UKR)"),
        ("/api/countries/UKR/forecast?days=7", "7-Day Risk Forecast (UKR)"),
        ("/api/countries/UKR/history?days=14", "Historical Risk Trajectory (UKR)"),
        ("/api/countries/UKR/summary", "Executive Summary Briefing (UKR)"),
        ("/api/countries/UKR/events?limit=5", "Recent Country Events (UKR)"),
        ("/api/risk/map", "Geospatial Risk Map"),
        ("/api/risk/export/geojson", "GIS RFC-7946 GeoJSON Export"),
        ("/api/trends?days=14", "Global Trends & Velocity Timeline"),
        ("/api/articles?page=1&page_size=5", "Paginated Deduplicated Articles"),
        ("/api/events?page=1&page_size=5", "Paginated Classified Events"),
        ("/api/events/export/csv", "Event Telemetry CSV Export"),
        ("/api/alerts?page=1&page_size=5", "Critical Alerts Log"),
        ("/api/alerts/webhooks/status", "Webhook Configuration Status"),
    ]

    passed = 0
    failed = 0

    for path, desc in get_endpoints:
        url = f"{base_url}{path}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                ct = resp.headers.get("content-type", "")
                if "application/json" in ct or "geo+json" in ct:
                    data = json.loads(resp.read().decode("utf-8"))
                    if isinstance(data, list):
                        detail = f"{len(data)} items"
                    elif isinstance(data, dict):
                        detail = f"{len(data)} keys ({', '.join(list(data.keys())[:3])}...)"
                    else:
                        detail = str(type(data))
                else:
                    raw = resp.read()
                    detail = f"{len(raw)} bytes ({ct.split(';')[0]})"

                print(f"[OK {status}] GET {path:<42} | {detail} ({desc})")
                passed += 1
        except Exception as e:
            print(f"[FAIL] GET {path:<42} | Error: {e} ({desc})")
            failed += 1

    print("=" * 70)
    print(f"Results: {passed} PASSED, {failed} FAILED across {passed + failed} verified endpoints.")
    print("=" * 70)


if __name__ == "__main__":
    verify_all_endpoints()
