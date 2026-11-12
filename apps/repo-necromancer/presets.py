"""Curated Legacy & AI-Generated Code Presets for RepoNecromancer (`apps/repo-necromancer`)."""

from __future__ import annotations
from typing import Any, Dict, List


REPO_NECROMANCER_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "RN-PRESET-01",
        "title": "Ghost Discount Overflow (Financial Invariant Bug)",
        "subtitle": "Unbounded discount rate yields negative checkout payable total",
        "code": (
            "def calculate_checkout_total(price: float, discount_rate: float) -> float:\n"
            "    # AI-generated checkout helper without boundary invariant guards\n"
            "    return round(price * (1.0 - discount_rate), 2)\n"
        ),
    },
    {
        "id": "RN-PRESET-02",
        "title": "Phantom Empty Telemetry (ZeroDivisionError on Empty Batch)",
        "subtitle": "Batch latency aggregator crashes when telemetry window is empty",
        "code": (
            "def compute_mean_latency(scores: list[float]) -> float:\n"
            "    total = sum(scores)\n"
            "    return total / len(scores)\n"
        ),
    },
    {
        "id": "RN-PRESET-03",
        "title": "Cryptographic Timing Oracle (CWE-208 Secret Leak)",
        "subtitle": "Short-circuit '==' comparison leaks webhook HMAC byte-by-byte",
        "code": (
            "def verify_token(provided_sig: str, expected_sig: str) -> bool:\n"
            "    return provided_sig == expected_sig\n"
        ),
    },
    {
        "id": "RN-PRESET-04",
        "title": "Necrotic Shell Conduit (CWE-78 OS Command Injection)",
        "subtitle": "Archive exporter passes unsanitized user path to shell=True",
        "code": (
            "import subprocess\n\n"
            "def export_log_bundle(filename: str) -> int:\n"
            "    proc = subprocess.Popen(f'tar -czf /tmp/out.tgz {filename}', shell=True)\n"
            "    return proc.wait()\n"
        ),
    },
    {
        "id": "RN-PRESET-05",
        "title": "Verified Safe Control: Bounded Discount Calculator",
        "subtitle": "Properly guarded function satisfying all EARS & Hypothesis invariants",
        "code": (
            "def calculate_safe_Position(value: float) -> float:\n"
            "    if value < 0.0:\n"
            "        return 0.0\n"
            "    return min(value, 1000.0)\n"
        ),
    },
]
