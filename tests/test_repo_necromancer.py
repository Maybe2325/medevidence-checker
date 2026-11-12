"""Unit & Integration Tests for Derived Application #1: RepoNecromancer (`apps/repo-necromancer`)."""

from __future__ import annotations

import pytest
from apps import repo_necromancer_adapter, repo_necromancer_presets
from packages.specguard_mcp_server.server import handle_mcp_request


@pytest.mark.integration
def test_repo_necromancer_presets_end_to_end() -> None:
    presets = repo_necromancer_presets.REPO_NECROMANCER_PRESETS
    assert len(presets) >= 5

    # First 4 presets have intentional bugs/vulnerabilities
    for preset in presets[:4]:
        report = repo_necromancer_adapter.audit_code_snippet(preset["code"], artifact_id=preset["id"])
        assert report.overall_status == "VIOLATION_DETECTED"
        assert any(w.violated for w in report.witnesses)

    # 5th preset is a verified safe control
    safe_preset = presets[4]
    safe_report = repo_necromancer_adapter.audit_code_snippet(
        safe_preset["code"], artifact_id=safe_preset["id"]
    )
    assert safe_report.overall_status == "VERIFIED_SAFE"


@pytest.mark.unit
def test_mcp_server_code_sandbox_tool_call() -> None:
    resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "tools/call",
            "params": {
                "name": "run_property_test_sandbox",
                "arguments": {
                    "source_code": "def ratio(a: float, divisor: float) -> float:\n    return a / divisor\n"
                },
            },
        }
    )
    structured = resp["result"]["structuredContent"]
    assert structured["status"] == "VIOLATION_DETECTED"
    assert any(f["rule_id"] == "PBT-ZERO-003" for f in structured["findings"])
