"""Standalone CLI Entrypoint for RepoNecromancer (`apps/repo-necromancer/cli.py`)."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps import repo_necromancer_adapter, repo_necromancer_presets  # noqa: E402


def main() -> int:
    preset = repo_necromancer_presets.REPO_NECROMANCER_PRESETS[0]
    report = repo_necromancer_adapter.audit_code_snippet(preset["code"], artifact_id=preset["id"])
    print(f"=== RepoNecromancer Audit Report ({report.artifact_id}) ===")
    print(f"Overall Status: {report.overall_status}")
    print(f"Compiled EARS Invariants: {report.compiled_invariants_count}")
    for w in report.witnesses:
        print(f"  - [{w.severity}] {w.witness_input} -> {w.observed_outcome}")
    print("\n--- Synthesized Verified Patch ---")
    print(report.patched_artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
