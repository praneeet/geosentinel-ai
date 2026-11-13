import urllib.request
import urllib.parse
import json
import sys

def verify_all_endpoints(base_url="http://127.0.0.1:8000"):
    print("=" * 70)
    print("GeoSentinel Enterprise — Comprehensive Endpoint Verification")
    print(f"Target Base URL: {base_url}")
    print("=" * 70)

    # 1. Login to get JWT Token
    token = None
    try:
        token_data = urllib.parse.urlencode({"username": "admin", "password": "admin123"}).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/auth/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            token = body.get("access_token")
            print(f"[OK 200] POST /api/auth/token -> Logged in as {body.get('role')} ({body.get('username')})")
    except Exception as e:
        print(f"[WARN] Auth login failed: {e}")

    auth_headers = {"Authorization": f"Bearer {token}"} if token else {}

    # List of GET endpoints to test
    get_endpoints = [
        ("/api/health", "System Health Probe"),
        ("/api/metrics", "Prometheus Telemetry"),
        ("/api/auth/roles", "RBAC Roles Directory"),
        ("/api/auth/me", "Current User Profile"),
        ("/api/countries", "Countries & Risk Indices"),
        ("/api/countries/UKR/risk", "Country Risk Score Detail (UKR)"),
        ("/api/countries/UKR/forecast?days=7", "7-Day Risk Forecast (UKR)"),
        ("/api/countries/UKR/history?days=14", "Historical Risk Trajectory (UKR)"),
        ("/api/countries/UKR/summary", "Executive Summary Briefing (UKR)"),
        ("/api/countries/UKR/events?limit=5", "Recent Country Events (UKR)"),
        ("/api/risk/map", "Geospatial Choropleth Risk Map"),
        ("/api/risk/export/geojson", "GIS RFC-7946 GeoJSON Export"),
        ("/api/trends?days=14", "Global Trends & Velocity Timeline"),
        ("/api/articles?page=1&page_size=5", "Paginated Deduplicated Articles"),
        ("/api/events?page=1&page_size=5", "Paginated Classified Events"),
        ("/api/events/export/csv", "Event Telemetry CSV Export"),
        ("/api/alerts?page=1&page_size=5", "Critical Alerts Log"),
        ("/api/assets", "Corporate Asset Geofences Registry"),
        ("/api/assets/asset-twn-fab18/threat-assessment", "Corporate Asset Threat Assessment"),
        ("/api/playbooks", "Operational Mitigation Playbooks Directory"),
        ("/api/playbooks/pb-red-sea-interdiction", "Red Sea Operational Playbook Detail"),
        ("/api/simulation/templates", "Tactical Scenario Templates"),
    ]

    passed = 0
    failed = 0

    for path, desc in get_endpoints:
        url = f"{base_url}{path}"
        try:
            req = urllib.request.Request(url, headers=auth_headers)
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

    # POST Endpoints to test
    post_tests = [
        (
            "/api/simulation/run",
            {"country_iso": "YEM", "scenario_title": "Chokepoint Strike Test", "category": "CONFLICT", "sentiment": -0.85, "credibility": 0.95, "injected_incidents_count": 3},
            "What-If Scenario Simulation",
        ),
        (
            "/api/chat",
            {"query": "Assess recent security conditions in Taiwan", "context_country_iso": "TWN"},
            "AI Copilot Analytical Briefing",
        ),
        (
            "/api/reports/generate",
            {"country_iso": "TWN"},
            "Strategic Intelligence Dossier Generation",
        ),
    ]

    for path, payload, desc in post_tests:
        url = f"{base_url}{path}"
        try:
            body = json.dumps(payload).encode("utf-8")
            headers = {"Content-Type": "application/json", **auth_headers}
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = resp.status
                data = json.loads(resp.read().decode("utf-8"))
                detail = f"{len(data)} keys"
                print(f"[OK {status}] POST {path:<41} | {detail} ({desc})")
                passed += 1
        except Exception as e:
            print(f"[FAIL] POST {path:<41} | Error: {e} ({desc})")
            failed += 1

    print("=" * 70)
    print(f"Results: {passed} PASSED, {failed} FAILED across {passed + failed} verified endpoints.")
    print("=" * 70)

if __name__ == "__main__":
    verify_all_endpoints()
