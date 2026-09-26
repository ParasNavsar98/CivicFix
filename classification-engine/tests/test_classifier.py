import json
import pytest
from typing import Optional, Dict, Any

from app.ai.provider import LLMProvider, LLMTimeoutException, LLMUnavailableException
from app.schemas.input import ProblemClassificationInput, ProblemLocation
from app.schemas.classification import StatusEnum
from app.services.classifier import ClassifierService


class MockLLMProvider(LLMProvider):
    """Mock LLM Provider for unit testing."""

    def __init__(self, response_text: str = "", exception_to_raise: Optional[Exception] = None):
        self.response_text = response_text
        self.exception_to_raise = exception_to_raise

    async def classify(
        self, prompt: str, response_schema: Optional[Dict[str, Any]] = None
    ) -> str:
        if self.exception_to_raise:
            raise self.exception_to_raise
        return self.response_text


@pytest.mark.asyncio
async def test_case_1_garbage_burning():
    mock_json = json.dumps({
        "problemSummary": "Garbage burning near school affecting residents",
        "primaryDomain": "Environment",
        "secondaryDomains": ["Sanitation"],
        "subcategory": "Pollution",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Waste Management"],
        "requiredResources": ["Waste Collection"],
        "confidence": 0.91,
        "reasoning": "Outdoor burning of waste causes severe air pollution."
    })
    mock_provider = MockLLMProvider(response_text=mock_json)
    service = ClassifierService(llm_provider=mock_provider)

    inp = ProblemClassificationInput(
        problemId="P1001",
        title="Garbage burning near school",
        description="People dump garbage near our school and burn it every evening. Smoke affects nearby residents.",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification is not None
    assert response.classification.primaryDomain == "Environment"
    assert response.classification.subcategory == "Pollution"


@pytest.mark.asyncio
async def test_case_2_water_pipeline_leakage():
    mock_json = json.dumps({
        "problemSummary": "Public water pipeline leaking continuously",
        "primaryDomain": "Water Resources",
        "secondaryDomains": [],
        "subcategory": "Leakage",
        "severity": "MEDIUM",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Civil Engineering"],
        "requiredResources": ["Pipeline Repair Kit"],
        "confidence": 0.90,
        "reasoning": "Clean water leakage requires prompt maintenance."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="P1002",
        title="Water pipeline leakage",
        description="A public water pipeline has been leaking continuously for several days.",
        location=ProblemLocation(district="Patna", state="Bihar"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Water Resources"
    assert response.classification.subcategory == "Leakage"


@pytest.mark.asyncio
async def test_case_3_cold_storage_farmers():
    mock_json = json.dumps({
        "problemSummary": "Lack of cold storage facilities causing crop loss",
        "primaryDomain": "Agriculture",
        "secondaryDomains": ["Rural Livelihoods"],
        "subcategory": "Storage",
        "severity": "HIGH",
        "urgency": "MEDIUM",
        "researchRequired": True,
        "governmentActionPossible": True,
        "requiredExpertise": ["Agri-Tech", "Cold Chain Logistics"],
        "requiredResources": ["Cold Storage Warehouse"],
        "confidence": 0.88,
        "reasoning": "Post-harvest crop loss requires agricultural storage solutions."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="P1003",
        title="No cold storage for farmers",
        description="Farmers in our area lose crops because there is no nearby cold storage facility.",
        location=ProblemLocation(district="Nashik", state="Maharashtra"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Agriculture"
    assert response.classification.subcategory == "Storage"


@pytest.mark.asyncio
async def test_case_4_broken_road():
    mock_json = json.dumps({
        "problemSummary": "Damaged road connecting village to highway",
        "primaryDomain": "Urban Infrastructure",
        "secondaryDomains": [],
        "subcategory": "Roads",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Road Construction"],
        "requiredResources": ["Asphalt", "Road Repair Machinery"],
        "confidence": 0.93,
        "reasoning": "Damaged transportation roads fall under infrastructure."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="P1004",
        title="Broken road",
        description="The road connecting our village to the main highway is badly damaged.",
        location=ProblemLocation(district="Jaipur", state="Rajasthan"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Urban Infrastructure"
    assert response.classification.subcategory == "Roads"


@pytest.mark.asyncio
async def test_case_5_hospital_diagnostic_equipment():
    mock_json = json.dumps({
        "problemSummary": "Local healthcare center lacks basic diagnostic equipment",
        "primaryDomain": "Healthcare",
        "secondaryDomains": [],
        "subcategory": "Diagnostics",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Medical Equipment Technician"],
        "requiredResources": ["Diagnostic Scanners"],
        "confidence": 0.89,
        "reasoning": "Medical facilities and diagnostics fall under healthcare."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="P1005",
        title="Hospital lacks diagnostic equipment",
        description="The local healthcare facility does not have necessary diagnostic equipment.",
        location=ProblemLocation(district="Bhopal", state="Madhya Pradesh"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Healthcare"
    assert response.classification.subcategory == "Diagnostics"


@pytest.mark.asyncio
async def test_case_6_ambiguous_input_low_confidence():
    mock_json = json.dumps({
        "problemSummary": "Unspecified village problem",
        "primaryDomain": "Other",
        "secondaryDomains": [],
        "subcategory": "Unclassified",
        "severity": "LOW",
        "urgency": "LOW",
        "researchRequired": False,
        "governmentActionPossible": False,
        "requiredExpertise": [],
        "requiredResources": [],
        "confidence": 0.40,  # Below threshold 0.85
        "reasoning": "Input is extremely vague and lacks specific details."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="P1006",
        title="Problem in our village",
        description="Everything is bad here.",
        location=ProblemLocation(district="Unknown", state="Unknown"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.REVIEW_REQUIRED
    assert response.classification.confidence == 0.40


@pytest.mark.asyncio
async def test_malformed_llm_json_response():
    service = ClassifierService(llm_provider=MockLLMProvider(response_text="Not a JSON string"))

    inp = ProblemClassificationInput(
        problemId="P1007",
        title="Garbage problem",
        description="Garbage in street",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.FAILED
    assert response.error.errorCode == "AI_INVALID_JSON"


@pytest.mark.asyncio
async def test_invalid_taxonomy_domain_from_llm():
    mock_json = json.dumps({
        "problemSummary": "Garbage burning near school",
        "primaryDomain": "InventedDomain",  # Invalid domain
        "secondaryDomains": [],
        "subcategory": "Pollution",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": [],
        "requiredResources": [],
        "confidence": 0.90,
        "reasoning": "Invalid taxonomy test"
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="P1008",
        title="Garbage problem",
        description="Garbage burning near school",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.FAILED
    assert response.error.errorCode == "INVALID_TAXONOMY_CATEGORY"


@pytest.mark.asyncio
async def test_llm_provider_timeout_failure():
    mock_provider = MockLLMProvider(exception_to_raise=LLMTimeoutException("Timed out"))
    service = ClassifierService(llm_provider=mock_provider)

    inp = ProblemClassificationInput(
        problemId="P1009",
        title="Garbage problem",
        description="Garbage burning near school",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.FAILED
    assert response.error.errorCode == "AI_PROVIDER_TIMEOUT"


@pytest.mark.asyncio
async def test_regression_case_1_unsafe_school_toilets_miss_classes():
    mock_json = json.dumps({
        "problemSummary": "Unsafe school toilets causing students to miss classes",
        "primaryDomain": "Sanitation",
        "secondaryDomains": [],  # Simulated raw LLM missing secondary domain
        "subcategory": "Toilets",
        "severity": "CRITICAL",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Sanitation Engineering"],
        "requiredResources": ["Construction Materials"],
        "confidence": 0.90,
        "reasoning": "Damaged toilets at school prevent students from attending class."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="CASE_1",
        title="Unsafe school toilets causing students to miss classes",
        description="The government school has severely damaged and unusable toilets. Students are frequently unable to attend classes because there are no functional sanitation facilities. The problem creates both a sanitation failure and a direct education access problem.",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Sanitation"
    assert response.classification.subcategory == "Toilets"
    assert "Education" in response.classification.secondaryDomains


@pytest.mark.asyncio
async def test_regression_case_2_garbage_burning_near_school_no_education_secondary():
    mock_json = json.dumps({
        "problemSummary": "Garbage burning near school",
        "primaryDomain": "Environment",
        "secondaryDomains": [],
        "subcategory": "Pollution",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Waste Management"],
        "requiredResources": ["Waste Collection"],
        "confidence": 0.90,
        "reasoning": "Garbage burning near school causes smoke exposure."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="CASE_2",
        title="Garbage burning near school",
        description="People are regularly burning garbage near the government school. Thick smoke enters the classrooms and students are exposed to the smoke during school hours.",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Environment"
    assert response.classification.subcategory == "Pollution"
    assert "Education" not in response.classification.secondaryDomains


@pytest.mark.asyncio
async def test_regression_case_3_broken_school_toilets_no_secondary():
    mock_json = json.dumps({
        "problemSummary": "Broken school toilets",
        "primaryDomain": "Sanitation",
        "secondaryDomains": [],
        "subcategory": "Toilets",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Plumbing"],
        "requiredResources": ["Sanitation Equipment"],
        "confidence": 0.92,
        "reasoning": "Facilities require repair."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="CASE_3",
        title="Broken school toilets",
        description="The government school toilets are damaged and unusable. The facilities require repair.",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Sanitation"
    assert response.classification.subcategory == "Toilets"
    assert response.classification.secondaryDomains == []


@pytest.mark.asyncio
async def test_regression_case_4_poor_school_sanitation_miss_classes():
    mock_json = json.dumps({
        "problemSummary": "Poor school sanitation causes students to miss classes",
        "primaryDomain": "Sanitation",
        "secondaryDomains": ["Education"],
        "subcategory": "Toilets",
        "severity": "CRITICAL",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Sanitation Engineering"],
        "requiredResources": ["Sanitation Supplies"],
        "confidence": 0.91,
        "reasoning": "Unusable toilets repeatedly prevent student attendance."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="CASE_4",
        title="Poor school sanitation causes students to miss classes",
        description="The school toilets are unusable because of severe sanitation problems. Students are repeatedly unable to attend classes because they cannot access functional sanitation facilities.",
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Sanitation"
    assert response.classification.subcategory == "Toilets"
    assert "Education" in response.classification.secondaryDomains


@pytest.mark.asyncio
async def test_regression_case_5_low_crop_prices_lack_irrigation():
    mock_json = json.dumps({
        "problemSummary": "Low crop prices and lack of irrigation",
        "primaryDomain": "Agriculture",
        "secondaryDomains": ["Rural Livelihoods"],
        "subcategory": "Irrigation",
        "severity": "HIGH",
        "urgency": "MEDIUM",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Agricultural Economics"],
        "requiredResources": ["Irrigation Pumps"],
        "confidence": 0.88,
        "reasoning": "Inadequate irrigation and market access difficulties impact farmers."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="CASE_5",
        title="Low crop prices and lack of irrigation",
        description="Farmers are simultaneously facing inadequate irrigation and difficulty accessing markets, resulting in crop losses and poor income.",
        location=ProblemLocation(district="Nashik", state="Maharashtra"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Agriculture"
    for sec in response.classification.secondaryDomains:
        assert sec in ["Rural Livelihoods", "Water Resources"]


@pytest.mark.asyncio
async def test_vague_indirect_stakeholder_impact_does_not_create_secondary():
    """Verify that indirect location/stakeholder presence does not force secondary domains."""
    mock_json = json.dumps({
        "problemSummary": "Potholes near hospital road",
        "primaryDomain": "Urban Infrastructure",
        "secondaryDomains": [],
        "subcategory": "Roads",
        "severity": "MEDIUM",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Civil Engineering"],
        "requiredResources": ["Asphalt"],
        "confidence": 0.90,
        "reasoning": "Potholes on public road."
    })
    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))

    inp = ProblemClassificationInput(
        problemId="STAKEHOLDER_TEST",
        title="Hospital road potholes",
        description="The main road outside the municipal hospital has several deep potholes. Vehicles and hospital visitors commute on this road.",
        location=ProblemLocation(district="Patna", state="Bihar"),
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.primaryDomain == "Urban Infrastructure"
    assert response.classification.subcategory == "Roads"
    assert "Healthcare" not in response.classification.secondaryDomains

