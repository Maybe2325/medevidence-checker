"""Quantitative Benchmark Evaluator (`Single-Prompt Baseline` vs `SpecGuard-Crew`)."""

from __future__ import annotations

from typing import Callable, Dict, List, Sequence
from .models import ConfusionMatrixMetrics


class BenchmarkEvaluator:
    """Computes bounded confusion matrix metrics with strict zero-division safety (Property 4)."""

    @staticmethod
    def compute_metrics(tp: int, fp: int, tn: int, fn: int) -> ConfusionMatrixMetrics:
        """
        Formal Correctness Property 4: Confusion Matrix Metric Bounds & Zero-Division Safety.
        All metrics are guaranteed to lie in [0.0, 1.0] for any non-negative integers tp, fp, tn, fn.
        """
        if tp < 0 or fp < 0 or tn < 0 or fn < 0:
            raise ValueError("Confusion matrix counts must be non-negative integers.")

        total = tp + fp + tn + fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0 if fn == 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0 if fp == 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 1.0
        f1_score = (
            (2.0 * precision * recall) / (precision + recall)
            if (precision + recall) > 0.0
            else 0.0
        )
        false_negative_rate = fn / (tp + fn) if (tp + fn) > 0 else 0.0
        accuracy = (tp + tn) / total if total > 0 else 1.0

        return ConfusionMatrixMetrics(
            tp=tp,
            fp=fp,
            tn=tn,
            fn=fn,
            total=total,
            precision=round(min(1.0, max(0.0, precision)), 4),
            recall=round(min(1.0, max(0.0, recall)), 4),
            specificity=round(min(1.0, max(0.0, specificity)), 4),
            f1_score=round(min(1.0, max(0.0, f1_score)), 4),
            false_negative_rate=round(min(1.0, max(0.0, false_negative_rate)), 4),
            accuracy=round(min(1.0, max(0.0, accuracy)), 4),
        )

    @classmethod
    def evaluate_predictions(
        cls,
        ground_truth_positive: Sequence[bool],
        predicted_positive: Sequence[bool],
    ) -> ConfusionMatrixMetrics:
        """Evaluate binary predictions against ground truth labels."""
        if len(ground_truth_positive) != len(predicted_positive):
            raise ValueError("Ground truth and prediction lists must have equal length.")

        tp = fp = tn = fn = 0
        for truth, pred in zip(ground_truth_positive, predicted_positive):
            if truth and pred:
                tp += 1
            elif not truth and pred:
                fp += 1
            elif not truth and not pred:
                tn += 1
            else:
                fn += 1

        return cls.compute_metrics(tp=tp, fp=fp, tn=tn, fn=fn)
