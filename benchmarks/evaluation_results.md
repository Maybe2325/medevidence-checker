# Quantitative Evaluation Report: Single-Prompt Baseline vs. SpecGuard-Crew

> Generated deterministically via `python3 benchmarks/run_evaluation.py`

## 1. App #1: `RepoNecromancer` (`benchmarks/dataset_code_bugs.json`, N=15)

| Method | TP | FP | TN | FN | Precision | Recall (Sensitivity) | Specificity | F1-Score | False Negative Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Single-Prompt Baseline** | 2 | 0 | 5 | 8 | 100.00% | 20.00% | 100.00% | 33.33% | 80.00% |
| **SpecGuard-Crew (Kiro + Hypothesis PBT)** | **10** | **0** | **5** | **0** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | **0.00%** |

## 2. App #2: `MedEvidence-Checker` (`benchmarks/dataset_clinical_cases.json`, N=20, Zero-PHI)

| Method | TP | FP | TN | FN | Precision | Recall (Sensitivity) | Specificity | F1-Score | False Negative Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Single-Prompt Baseline** | 1 | 0 | 8 | 11 | 100.00% | 8.33% | 100.00% | 15.38% | 91.67% |
| **SpecGuard-Crew (Kiro + MCP Guideline KB)** | **12** | **0** | **8** | **0** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | **0.00%** |
