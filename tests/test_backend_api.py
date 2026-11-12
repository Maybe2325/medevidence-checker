"""End-to-End FastAPI Backend & Workbench Integration Tests (`apps/backend_api/main.py`)."""

from __future__ import annotations

import asyncio
import httpx
import pytest

from apps.backend_api.main import app


def _request(method: str, path: str, json_body: dict | None = None) -> httpx.Response:
    async def _run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, json=json_body)

    return asyncio.run(_run())


@pytest.mark.integration
def test_backend_health_and_workbench_html() -> None:
    r_html = _request("GET", "/")
    assert r_html.status_code == 200
    assert "SpecGuard-Crew" in r_html.text

    r_health = _request("GET", "/api/health")
    assert r_health.status_code == 200
    data = r_health.json()
    assert data["status"] == "ok"
    assert data["zero_phi_enforced"] is True


@pytest.mark.integration
def test_backend_kiro_specs_and_benchmarks() -> None:
    r_specs = _request("GET", "/api/kiro/specs")
    assert r_specs.status_code == 200
    specs = r_specs.json()
    assert specs["total_specs"] == 3
    assert specs["total_clauses"] == 21

    r_bench = _request("GET", "/api/benchmarks")
    assert r_bench.status_code == 200
    bench = r_bench.json()
    assert bench["repo_necromancer"]["specguard_crew"]["f1_score"] == 1.0
    assert bench["med_evidence_checker"]["specguard_crew"]["f1_score"] == 1.0


@pytest.mark.integration
def test_backend_verify_code_and_clinical_endpoints() -> None:
    r_code = _request(
        "POST",
        "/api/verify/code",
        {
            "source_code": "def discount(price: float, rate: float) -> float:\n    return price * (1.0 - rate)\n",
            "artifact_id": "api-test-code",
        },
    )
    assert r_code.status_code == 200
    assert r_code.json()["report"]["overall_status"] == "VIOLATION_DETECTED"

    r_clin = _request(
        "POST",
        "/api/verify/clinical",
        {
            "clinical_text": "Synthetic note: 70yo patient, eGFR 20 mL/min/1.73m2. Plan: Start Metformin 1000 mg BID.",
            "artifact_id": "api-test-clin",
        },
    )
    assert r_clin.status_code == 200
    assert r_clin.json()["report"]["overall_status"] == "VIOLATION_DETECTED"
