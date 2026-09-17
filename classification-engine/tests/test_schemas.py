import pytest
from pydantic import ValidationError

from app.schemas.input import ProblemLocation, ProblemClassificationInput
from app.schemas.classification import (
    ClassificationResult,
    SeverityEnum,
    UrgencyEnum,
    StatusEnum,
)


def test_valid_input_schema():
    input_data = ProblemClassificationInput(
        problemId="P1001",
        title="  Garbage burning near school  ",
        description="People dump garbage near our school and burn it every evening.",
        location=ProblemLocation(
            district="Ranchi",
            state="Jharkhand",
            latitude=23.3441,
            longitude=85.3096,
        ),
    )
    assert input_data.problemId == "P1001"
    assert input_data.title == "Garbage burning near school"
    assert input_data.location.district == "Ranchi"


def test_empty_title_validation():
    with pytest.raises(ValidationError) as exc_info:
        ProblemClassificationInput(
            problemId="P1001",
            title="   ",
            description="Valid description",
            location=ProblemLocation(district="Ranchi", state="Jharkhand"),
        )
    assert "Field cannot be empty" in str(exc_info.value)


def test_empty_description_validation():
    with pytest.raises(ValidationError) as exc_info:
        ProblemClassificationInput(
            problemId="P1001",
            title="Valid title",
            description="",
            location=ProblemLocation(district="Ranchi", state="Jharkhand"),
        )
    assert "Field cannot be empty" in str(exc_info.value)


def test_invalid_location_latitude():
    with pytest.raises(ValidationError) as exc_info:
        ProblemLocation(
            district="Ranchi",
            state="Jharkhand",
            latitude=105.0,  # Invalid lat > 90
            longitude=85.0,
        )
    assert "Latitude must be between -90 and 90" in str(exc_info.value)


def test_invalid_location_longitude():
    with pytest.raises(ValidationError) as exc_info:
        ProblemLocation(
            district="Ranchi",
            state="Jharkhand",
            latitude=23.0,
            longitude=-200.0,  # Invalid lon < -180
        )
    assert "Longitude must be between -180 and 180" in str(exc_info.value)


def test_valid_classification_result():
    res = ClassificationResult(
        problemSummary="Garbage burning near school",
        primaryDomain="Environment",
        secondaryDomains=["Sanitation"],
        subcategory="Pollution",
        severity=SeverityEnum.HIGH,
        urgency=UrgencyEnum.HIGH,
        researchRequired=False,
        governmentActionPossible=True,
        requiredExpertise=["Waste Management"],
        requiredResources=["Waste Collection"],
        confidence=0.92,
        reasoning="Repeated open burning of garbage near a school.",
    )
    assert res.primaryDomain == "Environment"
    assert res.confidence == 0.92


def test_invalid_confidence_range():
    with pytest.raises(ValidationError):
        ClassificationResult(
            problemSummary="Test",
            primaryDomain="Environment",
            subcategory="Pollution",
            severity=SeverityEnum.LOW,
            urgency=UrgencyEnum.LOW,
            researchRequired=False,
            governmentActionPossible=True,
            confidence=1.5,  # Invalid confidence > 1.0
            reasoning="Test reasoning",
        )


def test_invalid_severity_enum():
    with pytest.raises(ValidationError):
        ClassificationResult(
            problemSummary="Test",
            primaryDomain="Environment",
            subcategory="Pollution",
            severity="EXTREME",  # Invalid enum value
            urgency=UrgencyEnum.LOW,
            researchRequired=False,
            governmentActionPossible=True,
            confidence=0.8,
            reasoning="Test reasoning",
        )


def test_invalid_urgency_enum():
    with pytest.raises(ValidationError):
        ClassificationResult(
            problemSummary="Test",
            primaryDomain="Environment",
            subcategory="Pollution",
            severity=SeverityEnum.HIGH,
            urgency="URGENT",  # Invalid enum value
            researchRequired=False,
            governmentActionPossible=True,
            confidence=0.8,
            reasoning="Test reasoning",
        )
