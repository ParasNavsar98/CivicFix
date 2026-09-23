"""
Phase 8 — Duplicate Metrics & Threshold Evaluation
Evaluates DuplicateDetector across 50 labeled cases in evaluation_dataset.json.
Measures Precision, Recall, F1 Score, False Positive Rate (FPR), and False Negative Rate (FNR)
across multiple candidate thresholds.
"""

import json
import os
import pytest
from app.services.duplicate_detector import DuplicateDetector
from app.services.embedding import EmbeddingService


@pytest.fixture(scope="module")
def evaluation_dataset():
    dataset_path = os.path.join(os.path.dirname(__file__), "evaluation_dataset.json")
    assert os.path.exists(dataset_path), f"Dataset file not found at {dataset_path}"
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def shared_embedding_service():
    service = EmbeddingService()
    service.load_model()
    return service


def evaluate_threshold(threshold: float, dataset: list, embedding_service: EmbeddingService):
    detector = DuplicateDetector(
        embedding_service=embedding_service,
        similarity_threshold=threshold
    )

    tp = fp = tn = fn = 0

    for case in dataset:
        prob_a = case["problem_a"]
        prob_b = case["problem_b"]
        expected_duplicate = case["expected_duplicate"]

        analysis = detector.analyze_candidate_pair(prob_a, prob_b)
        predicted_duplicate = analysis["candidateStatus"] in ("strong_candidate", "potential_duplicate")

        if expected_duplicate and predicted_duplicate:
            tp += 1
        elif not expected_duplicate and predicted_duplicate:
            fp += 1
        elif not expected_duplicate and not predicted_duplicate:
            tn += 1
        elif expected_duplicate and not predicted_duplicate:
            fn += 1

    total = len(dataset)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "threshold": threshold,
        "total": total,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
    }


def test_evaluate_threshold_matrix(evaluation_dataset, shared_embedding_service):
    thresholds = [0.60, 0.65, 0.70, 0.75, 0.78, 0.80, 0.85, 0.90]
    results = []

    print("\n" + "=" * 85)
    print("CIVICFIX DUPLICATE DETECTION EVALUATION REPORT (50 LABELED CASES)")
    print("=" * 85)
    print(f"{'Threshold':<10} | {'TP':<4} | {'FP':<4} | {'TN':<4} | {'FN':<4} | {'Precision':<10} | {'Recall':<10} | {'F1 Score':<10} | {'FPR':<8} | {'FNR':<8}")
    print("-" * 85)

    for thresh in thresholds:
        metrics = evaluate_threshold(thresh, evaluation_dataset, shared_embedding_service)
        results.append(metrics)
        print(
            f"{metrics['threshold']:<10.2f} | {metrics['tp']:<4} | {metrics['fp']:<4} | {metrics['tn']:<4} | {metrics['fn']:<4} | "
            f"{metrics['precision']:<10.4f} | {metrics['recall']:<10.4f} | {metrics['f1']:<10.4f} | {metrics['fpr']:<8.4f} | {metrics['fnr']:<8.4f}"
        )

    print("=" * 85)

    # Validate selected production default threshold 0.75
    default_metrics = [r for r in results if r["threshold"] == 0.75][0]
    assert default_metrics["precision"] >= 0.85, f"Precision too low: {default_metrics['precision']}"
    assert default_metrics["recall"] >= 0.85, f"Recall too low: {default_metrics['recall']}"
    assert default_metrics["f1"] >= 0.85, f"F1 score too low: {default_metrics['f1']}"
