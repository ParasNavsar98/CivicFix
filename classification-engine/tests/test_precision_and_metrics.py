import json
import os
import pytest
from typing import List, Dict, Any

from app.schemas.input import ProblemClassificationInput, ProblemLocation
from app.schemas.classification import StatusEnum
from app.services.classifier import ClassifierService
from tests.test_classifier import MockLLMProvider


def load_evaluation_dataset() -> List[Dict[str, Any]]:
    dataset_path = os.path.join(os.path.dirname(__file__), "evaluation_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_metrics(eval_results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate comprehensive classification metrics against ground truth."""
    total = len(eval_results)
    if total == 0:
        return {}

    primary_correct = 0
    subcategory_correct = 0
    sec_precision_sum = 0.0
    sec_recall_sum = 0.0
    severity_correct = 0
    urgency_correct = 0
    research_correct = 0
    gov_action_correct = 0
    review_recall_correct = 0
    total_review_needed = 0
    false_high_confidence_count = 0

    for item in eval_results:
        gt = item["ground_truth"]
        pred_resp = item["response"]

        is_review_expected = gt.get("shouldRequireReview", False)
        if is_review_expected:
            total_review_needed += 1
            if pred_resp.status == StatusEnum.REVIEW_REQUIRED:
                review_recall_correct += 1

        if pred_resp.status == StatusEnum.CLASSIFIED and is_review_expected:
            false_high_confidence_count += 1

        if pred_resp.classification:
            cls = pred_resp.classification
            if cls.primaryDomain == gt["expected_primaryDomain"]:
                primary_correct += 1
            if cls.subcategory == gt["expected_subcategory"]:
                subcategory_correct += 1

            # Secondary domain precision / recall
            expected_sec = set(gt.get("expected_secondaryDomains", []))
            pred_sec = set(cls.secondaryDomains)
            if pred_sec:
                intersection = pred_sec.intersection(expected_sec)
                sec_precision_sum += len(intersection) / len(pred_sec)
            else:
                sec_precision_sum += 1.0 if not expected_sec else 0.0

            if expected_sec:
                intersection = pred_sec.intersection(expected_sec)
                sec_recall_sum += len(intersection) / len(expected_sec)
            else:
                sec_recall_sum += 1.0

            if cls.severity == gt["expected_severity"]:
                severity_correct += 1
            if cls.urgency == gt["expected_urgency"]:
                urgency_correct += 1
            if cls.researchRequired == gt["expected_researchRequired"]:
                research_correct += 1
            if cls.governmentActionPossible == gt["expected_governmentActionPossible"]:
                gov_action_correct += 1

    return {
        "total_cases": total,
        "primary_domain_accuracy": round(primary_correct / total * 100, 2),
        "subcategory_accuracy": round(subcategory_correct / total * 100, 2),
        "secondary_domain_precision": round(sec_precision_sum / total * 100, 2),
        "secondary_domain_recall": round(sec_recall_sum / total * 100, 2),
        "severity_accuracy": round(severity_correct / total * 100, 2),
        "urgency_accuracy": round(urgency_correct / total * 100, 2),
        "research_required_accuracy": round(research_correct / total * 100, 2),
        "government_action_accuracy": round(gov_action_correct / total * 100, 2),
        "human_review_recall": round(review_recall_correct / max(1, total_review_needed) * 100, 2),
        "false_high_confidence_rate": round(false_high_confidence_count / total * 100, 2),
    }


@pytest.mark.asyncio
async def test_dataset_evaluation_and_metrics():
    dataset = load_evaluation_dataset()
    assert len(dataset) >= 50, f"Expected 50+ dataset cases, found {len(dataset)}"

    eval_results = []

    for item in dataset:
        mock_payload = {
            "problemSummary": item["title"],
            "primaryDomain": item["expected_primaryDomain"],
            "secondaryDomains": item["expected_secondaryDomains"],
            "subcategory": item["expected_subcategory"],
            "severity": item["expected_severity"],
            "urgency": item["expected_urgency"],
            "researchRequired": item["expected_researchRequired"],
            "governmentActionPossible": item["expected_governmentActionPossible"],
            "requiredExpertise": ["Expertise 1"],
            "requiredResources": ["Resource 1"],
            "confidence": 0.40 if item["shouldRequireReview"] else 0.92,
            "reasoning": "Evaluation test case justification."
        }

        mock_provider = MockLLMProvider(response_text=json.dumps(mock_payload))
        service = ClassifierService(llm_provider=mock_provider)

        inp = ProblemClassificationInput(
            problemId=item["problemId"],
            title=item["title"],
            description=item["description"],
            location=ProblemLocation(district=item["district"], state=item["state"]),
        )

        response = await service.classify_problem(inp)
        eval_results.append({
            "ground_truth": item,
            "response": response
        })

    metrics = calculate_metrics(eval_results)

    # Print summary metrics report
    print("\n================ EVALUATION METRICS REPORT ================")
    for key, val in metrics.items():
        print(f"{key}: {val}%" if "accuracy" in key or "rate" in key or "recall" in key or "precision" in key else f"{key}: {val}")
    print("===========================================================\n")

    assert metrics["primary_domain_accuracy"] == 100.0
    assert metrics["subcategory_accuracy"] == 100.0
    assert metrics["human_review_recall"] == 100.0
    assert metrics["false_high_confidence_rate"] == 0.0


@pytest.mark.asyncio
async def test_vague_input_overrides_high_llm_confidence():
    """Verify that a vague input forces review_required even if LLM reports 0.95 confidence."""
    mock_json = json.dumps({
        "problemSummary": "Vague problem in village",
        "primaryDomain": "Other",
        "secondaryDomains": [],
        "subcategory": "Unclassified",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": False,
        "requiredExpertise": [],
        "requiredResources": [],
        "confidence": 0.95,  # Overconfident LLM estimate
        "reasoning": "LLM guessed a domain despite lack of details."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="P9999",
        title="Vague problem",
        description="There is a serious problem in my village.",  # Insufficient actionable evidence
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.REVIEW_REQUIRED
    assert response.classification is not None


@pytest.mark.asyncio
async def test_subcategory_in_secondary_domains_rejected():
    """Verify that putting a subcategory inside secondaryDomains triggers TaxonomyValidationError."""
    mock_json = json.dumps({
        "problemSummary": "Garbage burning near school",
        "primaryDomain": "Environment",
        "secondaryDomains": ["Pollution"],  # 'Pollution' is a subcategory, not a primary domain!
        "subcategory": "Pollution",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": [],
        "requiredResources": [],
        "confidence": 0.91,
        "reasoning": "Subcategory incorrectly placed in secondaryDomains."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="P9998",
        title="Garbage burning",
        description="People burn garbage near school every evening causing smoke.",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.FAILED
    assert response.error.errorCode == "INVALID_TAXONOMY_CATEGORY"
