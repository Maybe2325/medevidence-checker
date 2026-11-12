"""Reproducible Quantitative Evaluation Script (`Single-Prompt Baseline` vs `SpecGuard-Crew`)."""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any, Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps import med_evidence_adapter, repo_necromancer_adapter  # noqa: E402
from packages.specguard_core.evaluator import BenchmarkEvaluator  # noqa: E402


def run_all_benchmarks() -> Dict[str, Any]:
    bench_dir = ROOT / "benchmarks"
    code_cases: List[Dict[str, Any]] = json.loads(
        (bench_dir / "dataset_code_bugs.json").read_text(encoding="utf-8")
    )
    clinical_cases: List[Dict[str, Any]] = json.loads(
        (bench_dir / "dataset_clinical_cases.json").read_text(encoding="utf-8")
    )

    # 1. Evaluate App #1: RepoNecromancer (15 code samples)
    code_truth = [bool(c["has_violation"]) for c in code_cases]
    code_base_preds = [
        repo_necromancer_adapter.run_single_prompt_code_baseline(c["code"])
        for c in code_cases
    ]
    code_crew_preds = [
        repo_necromancer_adapter.audit_code_snippet(c["code"], artifact_id=c["id"]).overall_status
        == "VIOLATION_DETECTED"
        for c in code_cases
    ]

    code_base_metrics = BenchmarkEvaluator.evaluate_predictions(code_truth, code_base_preds)
    code_crew_metrics = BenchmarkEvaluator.evaluate_predictions(code_truth, code_crew_preds)

    # 2. Evaluate App #2: MedEvidence-Checker (20 synthetic clinical cases)
    clin_truth = [bool(c["has_violation"]) for c in clinical_cases]
    clin_base_preds = [
        med_evidence_adapter.run_single_prompt_clinical_baseline(c["clinical_text"])
        for c in clinical_cases
    ]
    clin_crew_preds = [
        med_evidence_adapter.audit_clinical_note(c["clinical_text"], artifact_id=c["id"]).overall_status
        == "VIOLATION_DETECTED"
        for c in clinical_cases
    ]

    clin_base_metrics = BenchmarkEvaluator.evaluate_predictions(clin_truth, clin_base_preds)
    clin_crew_metrics = BenchmarkEvaluator.evaluate_predictions(clin_truth, clin_crew_preds)

    results = {
        "repo_necromancer": {
            "dataset_size": len(code_cases),
            "positive_violations": sum(code_truth),
            "safe_controls": len(code_truth) - sum(code_truth),
            "single_prompt_baseline": code_base_metrics.model_dump(),
            "specguard_crew": code_crew_metrics.model_dump(),
        },
        "med_evidence_checker": {
            "dataset_size": len(clinical_cases),
            "positive_violations": sum(clin_truth),
            "safe_controls": len(clin_truth) - sum(clin_truth),
            "single_prompt_baseline": clin_base_metrics.model_dump(),
            "specguard_crew": clin_crew_metrics.model_dump(),
        },
    }

    (bench_dir / "evaluation_results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )

    md_report = f"""# Quantitative Evaluation Report: Single-Prompt Baseline vs. SpecGuard-Crew

> Generated deterministically via `python3 benchmarks/run_evaluation.py`

## 1. App #1: `RepoNecromancer` (`benchmarks/dataset_code_bugs.json`, N={len(code_cases)})

| Method | TP | FP | TN | FN | Precision | Recall (Sensitivity) | Specificity | F1-Score | False Negative Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Single-Prompt Baseline** | {code_base_metrics.tp} | {code_base_metrics.fp} | {code_base_metrics.tn} | {code_base_metrics.fn} | {code_base_metrics.precision:.2%} | {code_base_metrics.recall:.2%} | {code_base_metrics.specificity:.2%} | {code_base_metrics.f1_score:.2%} | {code_base_metrics.false_negative_rate:.2%} |
| **SpecGuard-Crew (Kiro + Hypothesis PBT)** | **{code_crew_metrics.tp}** | **{code_crew_metrics.fp}** | **{code_crew_metrics.tn}** | **{code_crew_metrics.fn}** | **{code_crew_metrics.precision:.2%}** | **{code_crew_metrics.recall:.2%}** | **{code_crew_metrics.specificity:.2%}** | **{code_crew_metrics.f1_score:.2%}** | **{code_crew_metrics.false_negative_rate:.2%}** |

## 2. App #2: `MedEvidence-Checker` (`benchmarks/dataset_clinical_cases.json`, N={len(clinical_cases)}, Zero-PHI)

| Method | TP | FP | TN | FN | Precision | Recall (Sensitivity) | Specificity | F1-Score | False Negative Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Single-Prompt Baseline** | {clin_base_metrics.tp} | {clin_base_metrics.fp} | {clin_base_metrics.tn} | {clin_base_metrics.fn} | {clin_base_metrics.precision:.2%} | {clin_base_metrics.recall:.2%} | {clin_base_metrics.specificity:.2%} | {clin_base_metrics.f1_score:.2%} | {clin_base_metrics.false_negative_rate:.2%} |
| **SpecGuard-Crew (Kiro + MCP Guideline KB)** | **{clin_crew_metrics.tp}** | **{clin_crew_metrics.fp}** | **{clin_crew_metrics.tn}** | **{clin_crew_metrics.fn}** | **{clin_crew_metrics.precision:.2%}** | **{clin_crew_metrics.recall:.2%}** | **{clin_crew_metrics.specificity:.2%}** | **{clin_crew_metrics.f1_score:.2%}** | **{clin_crew_metrics.false_negative_rate:.2%}** |
"""
    (bench_dir / "evaluation_results.md").write_text(md_report, encoding="utf-8")
    print(md_report)
    return results


if __name__ == "__main__":
    run_all_benchmarks()
