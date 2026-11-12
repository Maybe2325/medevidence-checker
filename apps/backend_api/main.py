"""FastAPI Unified Backend API serving RepoNecromancer, MedEvidence-Checker, .kiro Inspector, and Web Workbench."""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from apps import (
    med_evidence_adapter,
    med_evidence_presets,
    repo_necromancer_adapter,
    repo_necromancer_presets,
)
from packages.specguard_core.compiler import EARSCompiler


ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKBENCH_HTML = ROOT / "apps" / "web-workbench" / "index.html"

app = FastAPI(
    title="SpecGuard-Crew Unified Verification API",
    version="0.1.0",
    description="Kiro Skeleton Crew API powering RepoNecromancer (App #1) and MedEvidence-Checker (App #2).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeVerifyRequest(BaseModel):
    source_code: str
    artifact_id: str = "live-code-audit"


class ClinicalVerifyRequest(BaseModel):
    clinical_text: str
    artifact_id: str = "live-clinical-audit"


@app.get("/", response_class=HTMLResponse)
def serve_workbench() -> Any:
    """Serve the interactive Dual-Theme Web Workbench."""
    if WORKBENCH_HTML.exists():
        return FileResponse(WORKBENCH_HTML, media_type="text/html")
    return HTMLResponse("<h1>SpecGuard-Crew API is running.</h1>")


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "project": "SpecGuard-Crew",
        "skeleton": "packages/specguard_core",
        "apps": ["apps/repo-necromancer", "apps/med-evidence-checker"],
        "zero_phi_enforced": True,
    }


@app.get("/api/kiro/specs")
def get_kiro_specs() -> Dict[str, Any]:
    """Return all compiled .kiro/specs EARS VerificationDAGs and .kiro manifest metadata."""
    compiler = EARSCompiler()
    spec_files = sorted(ROOT.glob(".kiro/specs/*/requirements.md"))
    dags = [compiler.compile_file(p).model_dump() for p in spec_files]
    return {
        "total_specs": len(dags),
        "total_clauses": sum(len(d["clauses"]) for d in dags),
        "dags": dags,
        "hooks": [p.name for p in sorted((ROOT / ".kiro" / "hooks").glob("*.yaml"))],
        "steering": [p.name for p in sorted((ROOT / ".kiro" / "steering").glob("*.md"))],
        "agents": [p.name for p in sorted((ROOT / ".kiro" / "agents").glob("*.yaml"))],
        "powers": [p.parent.name for p in sorted((ROOT / ".kiro" / "powers").glob("*/POWER.md"))],
    }


@app.get("/api/presets")
def get_all_presets() -> Dict[str, Any]:
    return {
        "repo_necromancer": repo_necromancer_presets.REPO_NECROMANCER_PRESETS,
        "med_evidence_checker": med_evidence_presets.MED_EVIDENCE_PRESETS,
    }


@app.post("/api/verify/code")
def verify_code(req: CodeVerifyRequest) -> Dict[str, Any]:
    report = repo_necromancer_adapter.audit_code_snippet(
        req.source_code, artifact_id=req.artifact_id
    )
    baseline_flagged = repo_necromancer_adapter.run_single_prompt_code_baseline(req.source_code)
    return {
        "report": report.model_dump(),
        "single_prompt_baseline_flagged": baseline_flagged,
    }


@app.post("/api/verify/clinical")
def verify_clinical(req: ClinicalVerifyRequest) -> Dict[str, Any]:
    report = med_evidence_adapter.audit_clinical_note(
        req.clinical_text, artifact_id=req.artifact_id
    )
    baseline_flagged = med_evidence_adapter.run_single_prompt_clinical_baseline(req.clinical_text)
    return {
        "report": report.model_dump(),
        "single_prompt_baseline_flagged": baseline_flagged,
    }


@app.get("/api/benchmarks")
def get_benchmarks() -> Dict[str, Any]:
    res_file = ROOT / "benchmarks" / "evaluation_results.json"
    if res_file.exists():
        return json.loads(res_file.read_text(encoding="utf-8"))
    return {}
