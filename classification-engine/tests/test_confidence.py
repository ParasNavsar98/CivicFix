import pytest
from app.services.confidence import evaluate_confidence
from app.schemas.classification import StatusEnum


def test_high_confidence_classification():
    status = evaluate_confidence(0.95)
    assert status == StatusEnum.CLASSIFIED

    exact_status = evaluate_confidence(0.85)
    assert exact_status == StatusEnum.CLASSIFIED


def test_low_confidence_review_required():
    status = evaluate_confidence(0.84)
    assert status == StatusEnum.REVIEW_REQUIRED

    very_low_status = evaluate_confidence(0.40)
    assert very_low_status == StatusEnum.REVIEW_REQUIRED
