import json
import pytest
from app.schemas.input import ProblemClassificationInput, ProblemLocation
from app.schemas.classification import (
    StatusEnum,
    SeverityEnum,
    UrgencyEnum,
    HealthSafetyImpactEnum,
    ExposureScopeEnum,
    VulnerablePopulationExposureEnum,
    GeographicExtentEnum,
    DurationEnum,
    InfrastructureImpactEnum,
    EnvironmentalImpactEnum,
    SocialEconomicImpactEnum,
    ReversibilityEnum,
    PeopleAffectedSourceEnum,
)
from app.services.classifier import ClassifierService
from tests.test_classifier import MockLLMProvider


@pytest.mark.asyncio
async def test_case_1_vague_problem():
    """Scenario 1: Vague problem statement should yield UNKNOWN factors, low confidence, and review_required."""
    mock_json = json.dumps({
        "problemSummary": "Unspecified problem reported in village",
        "primaryDomain": "Other",
        "secondaryDomains": [],
        "subcategory": "Unclassified",
        "severity": "LOW",
        "severityAssessment": {
            "healthSafetyImpact": "UNKNOWN",
            "exposureScope": "UNKNOWN",
            "vulnerablePopulationExposure": "UNKNOWN",
            "geographicExtent": "UNKNOWN",
            "duration": "UNKNOWN",
            "infrastructureImpact": "UNKNOWN",
            "environmentalImpact": "UNKNOWN",
            "socialEconomicImpact": "UNKNOWN",
            "reversibility": "UNKNOWN"
        },
        "severityEvidence": ["No specific details provided in problem description."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "LOW",
        "researchRequired": False,
        "governmentActionPossible": False,
        "requiredExpertise": [],
        "requiredResources": [],
        "confidence": 0.35,
        "reasoning": "Input is extremely vague and lacks specific evidence."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2001",
        title="Problem in village",
        description="There is a problem in my village.",
        location=ProblemLocation(district="Ranchi", state="Jharkhand")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.REVIEW_REQUIRED
    assert response.classification is not None
    assert response.classification.severityAssessment.exposureScope == ExposureScopeEnum.UNKNOWN
    assert response.classification.peopleAffected.source == PeopleAffectedSourceEnum.NOT_PROVIDED
    assert response.classification.peopleAffected.value is None


@pytest.mark.asyncio
async def test_case_2_localized_problem():
    """Scenario 2: Pothole outside house should yield LOCAL scope, SINGLE_LOCATION extent, and no population count."""
    mock_json = json.dumps({
        "problemSummary": "Single pothole on road outside residential house",
        "primaryDomain": "Urban Infrastructure",
        "secondaryDomains": [],
        "subcategory": "Roads",
        "severity": "LOW",
        "severityAssessment": {
            "healthSafetyImpact": "LOW",
            "exposureScope": "LOCAL",
            "vulnerablePopulationExposure": "NONE_IDENTIFIED",
            "geographicExtent": "SINGLE_LOCATION",
            "duration": "UNKNOWN",
            "infrastructureImpact": "LOW",
            "environmentalImpact": "NONE",
            "socialEconomicImpact": "NONE",
            "reversibility": "EASILY_REVERSIBLE"
        },
        "severityEvidence": ["Pothole located specifically outside citizen's house."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "LOW",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Road Construction"],
        "requiredResources": ["Asphalt"],
        "confidence": 0.92,
        "reasoning": "Minor road surface defect isolated to a single residential location."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2002",
        title="Pothole outside my house",
        description="There is a pothole outside my house causing minor inconvenience.",
        location=ProblemLocation(district="Patna", state="Bihar")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severityAssessment.exposureScope == ExposureScopeEnum.LOCAL
    assert response.classification.severityAssessment.geographicExtent == GeographicExtentEnum.SINGLE_LOCATION
    assert response.classification.peopleAffected.value is None


@pytest.mark.asyncio
async def test_case_3_school_children_exposure():
    """Scenario 3: Garbage burning beside school should indicate vulnerable population exposure and persistent duration."""
    mock_json = json.dumps({
        "problemSummary": "Garbage burning near school creating smoke hazard for students",
        "primaryDomain": "Environment",
        "secondaryDomains": ["Sanitation", "Healthcare"],
        "subcategory": "Pollution",
        "severity": "HIGH",
        "severityAssessment": {
            "healthSafetyImpact": "HIGH",
            "exposureScope": "COMMUNITY",
            "vulnerablePopulationExposure": "CLEAR",
            "geographicExtent": "LOCAL_AREA",
            "duration": "PERSISTENT",
            "infrastructureImpact": "NONE",
            "environmentalImpact": "HIGH",
            "socialEconomicImpact": "LOW",
            "reversibility": "RECOVERABLE"
        },
        "severityEvidence": [
            "Garbage is burned beside a school every evening.",
            "School children are exposed to toxic smoke."
        ],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Waste Management"],
        "requiredResources": ["Waste Collection Vehicle"],
        "confidence": 0.89,
        "reasoning": "Regular toxic burning near a school directly exposes children."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2003",
        title="Garbage burning near school",
        description="Garbage is being burned beside a school every evening.",
        location=ProblemLocation(district="Ranchi", state="Jharkhand")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severityAssessment.vulnerablePopulationExposure == VulnerablePopulationExposureEnum.CLEAR
    assert response.classification.severityAssessment.exposureScope == ExposureScopeEnum.COMMUNITY
    assert response.classification.peopleAffected.value is None  # Student count was NOT fabricated


@pytest.mark.asyncio
async def test_case_4_health_emergency_gas_leak():
    """Scenario 4: Gas leak in school should yield HIGH/CRITICAL health impact with UNKNOWN student count."""
    mock_json = json.dumps({
        "problemSummary": "Gas leak reported inside school building",
        "primaryDomain": "Healthcare",
        "secondaryDomains": ["Education"],
        "subcategory": "Public Health",
        "severity": "CRITICAL",
        "severityAssessment": {
            "healthSafetyImpact": "CRITICAL",
            "exposureScope": "COMMUNITY",
            "vulnerablePopulationExposure": "CLEAR",
            "geographicExtent": "SINGLE_LOCATION",
            "duration": "SHORT_TERM",
            "infrastructureImpact": "HIGH",
            "environmentalImpact": "MODERATE",
            "socialEconomicImpact": "NONE",
            "reversibility": "EASILY_REVERSIBLE"
        },
        "severityEvidence": [
            "Gas leak reported inside a school facility.",
            "Immediate physical danger to students and school staff."
        ],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "CRITICAL",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Hazardous Material Response", "Fire & Safety"],
        "requiredResources": ["Gas Leak Shutoff Equipment"],
        "confidence": 0.94,
        "reasoning": "Hazardous chemical leak in educational facility requires immediate critical action."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2004",
        title="Gas leak in school",
        description="A gas leak has been reported inside a school.",
        location=ProblemLocation(district="Bhopal", state="Madhya Pradesh")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severity == SeverityEnum.CRITICAL
    assert response.classification.severityAssessment.healthSafetyImpact == HealthSafetyImpactEnum.CRITICAL
    assert response.classification.peopleAffected.source == PeopleAffectedSourceEnum.NOT_PROVIDED


@pytest.mark.asyncio
async def test_case_5_large_area_infrastructure_issue():
    """Scenario 5: Village water supply outage for 5 days should indicate COMMUNITY scope, ONGOING/LONG_TERM duration, and HIGH infrastructure impact."""
    mock_json = json.dumps({
        "problemSummary": "Entire village water supply outage for 5 days",
        "primaryDomain": "Water Resources",
        "secondaryDomains": ["Healthcare"],
        "subcategory": "Supply",
        "severity": "HIGH",
        "severityAssessment": {
            "healthSafetyImpact": "HIGH",
            "exposureScope": "COMMUNITY",
            "vulnerablePopulationExposure": "POSSIBLE",
            "geographicExtent": "WIDE_AREA",
            "duration": "LONG_TERM",
            "infrastructureImpact": "HIGH",
            "environmentalImpact": "LOW",
            "socialEconomicImpact": "HIGH",
            "reversibility": "RECOVERABLE"
        },
        "severityEvidence": [
            "Water supply unavailable across entire village.",
            "Disruption has persisted for 5 days."
        ],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Hydraulic Engineering"],
        "requiredResources": ["Water Tankers", "Pumping Equipment"],
        "confidence": 0.91,
        "reasoning": "Extended total loss of drinking water supply across an entire village."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2005",
        title="Water supply unavailable",
        description="The water supply has been unavailable across the entire village for five days.",
        location=ProblemLocation(district="Jaipur", state="Rajasthan")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severityAssessment.infrastructureImpact == InfrastructureImpactEnum.HIGH
    assert response.classification.severityAssessment.duration == DurationEnum.LONG_TERM
    assert response.classification.peopleAffected.value is None


@pytest.mark.asyncio
async def test_case_6_environmental_damage():
    """Scenario 6: Chemical waste dumped into river should reflect HIGH/CRITICAL environmental impact."""
    mock_json = json.dumps({
        "problemSummary": "Industrial chemical waste dumped into river",
        "primaryDomain": "Environment",
        "secondaryDomains": ["Water Resources"],
        "subcategory": "Pollution",
        "severity": "HIGH",
        "severityAssessment": {
            "healthSafetyImpact": "HIGH",
            "exposureScope": "LARGE_AREA",
            "vulnerablePopulationExposure": "POSSIBLE",
            "geographicExtent": "WIDE_AREA",
            "duration": "ONGOING",
            "infrastructureImpact": "NONE",
            "environmentalImpact": "HIGH",
            "socialEconomicImpact": "MODERATE",
            "reversibility": "DIFFICULT_TO_RECOVER"
        },
        "severityEvidence": ["Toxic chemical discharge into public watercourse."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "HIGH",
        "researchRequired": True,
        "governmentActionPossible": True,
        "requiredExpertise": ["Environmental Chemistry", "Water Remediation"],
        "requiredResources": ["Water Quality Testing Kits"],
        "confidence": 0.88,
        "reasoning": "Chemical contamination of water system causes severe ecosystem damage."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2006",
        title="Chemical waste in river",
        description="A factory is dumping chemical waste into the local river.",
        location=ProblemLocation(district="Kanpur", state="Uttar Pradesh")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severityAssessment.environmentalImpact == EnvironmentalImpactEnum.HIGH
    assert response.classification.severityAssessment.reversibility == ReversibilityEnum.DIFFICULT_TO_RECOVER


@pytest.mark.asyncio
async def test_case_7_social_economic_livelihood_issue():
    """Scenario 7: Farmers unable to sell crops due to collapsed bridge -> HIGH socialEconomicImpact."""
    mock_json = json.dumps({
        "problemSummary": "Bridge collapse prevents farmers from accessing market to sell crops",
        "primaryDomain": "Agriculture",
        "secondaryDomains": ["Urban Infrastructure", "Rural Livelihoods"],
        "subcategory": "Market Linkage",
        "severity": "HIGH",
        "severityAssessment": {
            "healthSafetyImpact": "MODERATE",
            "exposureScope": "COMMUNITY",
            "vulnerablePopulationExposure": "NONE_IDENTIFIED",
            "geographicExtent": "LOCAL_AREA",
            "duration": "ONGOING",
            "infrastructureImpact": "HIGH",
            "environmentalImpact": "NONE",
            "socialEconomicImpact": "HIGH",
            "reversibility": "RECOVERABLE"
        },
        "severityEvidence": ["Bridge collapse isolates farmers from crop market access."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Structural Engineering", "Rural Development"],
        "requiredResources": ["Temporary Bridge Structure"],
        "confidence": 0.90,
        "reasoning": "Loss of critical bridge cuts off agrarian livelihood transport."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2007",
        title="Farmers cannot sell crops",
        description="Farmers cannot sell their crops because the main connecting bridge collapsed.",
        location=ProblemLocation(district="Nashik", state="Maharashtra")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severityAssessment.socialEconomicImpact == SocialEconomicImpactEnum.HIGH


@pytest.mark.asyncio
async def test_case_8_missing_population_number():
    """Scenario 8: Missing population number must result in source NOT_PROVIDED and value null."""
    mock_json = json.dumps({
        "problemSummary": "Streetlight failure in residential colony",
        "primaryDomain": "Urban Infrastructure",
        "secondaryDomains": [],
        "subcategory": "Streetlights",
        "severity": "LOW",
        "severityAssessment": {
            "healthSafetyImpact": "LOW",
            "exposureScope": "LOCAL",
            "vulnerablePopulationExposure": "NONE_IDENTIFIED",
            "geographicExtent": "SINGLE_LOCATION",
            "duration": "SHORT_TERM",
            "infrastructureImpact": "LOW",
            "environmentalImpact": "NONE",
            "socialEconomicImpact": "NONE",
            "reversibility": "EASILY_REVERSIBLE"
        },
        "severityEvidence": ["Streetlight out on main street."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "LOW",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Electrical Repair"],
        "requiredResources": ["Streetlight Bulb"],
        "confidence": 0.91,
        "reasoning": "Routine electrical maintenance issue."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2008",
        title="Streetlight broken",
        description="The streetlight near the corner store is broken.",
        location=ProblemLocation(district="Lucknow", state="Uttar Pradesh")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.peopleAffected.source == PeopleAffectedSourceEnum.NOT_PROVIDED
    assert response.classification.peopleAffected.value is None
    assert response.classification.peopleAffected.unit is None


@pytest.mark.asyncio
async def test_case_9_explicit_population_number_families():
    """Scenario 9: Explicitly reported population count (e.g. 200 families) must preserve value, unit, and source CITIZEN_REPORTED without unit conversion."""
    mock_json = json.dumps({
        "problemSummary": "Water pipeline leakage affecting 200 families for 3 days",
        "primaryDomain": "Water Resources",
        "secondaryDomains": [],
        "subcategory": "Leakage",
        "severity": "MEDIUM",
        "severityAssessment": {
            "healthSafetyImpact": "MODERATE",
            "exposureScope": "COMMUNITY",
            "vulnerablePopulationExposure": "NONE_IDENTIFIED",
            "geographicExtent": "LOCAL_AREA",
            "duration": "ONGOING",
            "infrastructureImpact": "MODERATE",
            "environmentalImpact": "LOW",
            "socialEconomicImpact": "LOW",
            "reversibility": "RECOVERABLE"
        },
        "severityEvidence": [
            "Water pipeline leakage ongoing for 3 days.",
            "Citizen explicitly reported 200 families affected."
        ],
        "peopleAffected": {
            "value": 200,
            "unit": "families",
            "source": "CITIZEN_REPORTED"
        },
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Plumbing", "Civil Engineering"],
        "requiredResources": ["Pipe Repair Clamp"],
        "confidence": 0.92,
        "reasoning": "Pipeline leak affecting reported residential families."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2009",
        title="Water leakage affecting 200 families",
        description="Water has been leaking for 3 days and around 200 families are affected.",
        location=ProblemLocation(district="Indore", state="Madhya Pradesh")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.peopleAffected.value == 200
    assert response.classification.peopleAffected.unit == "families"
    assert response.classification.peopleAffected.source == PeopleAffectedSourceEnum.CITIZEN_REPORTED


@pytest.mark.asyncio
async def test_case_10_missing_duration():
    """Scenario 10: Problem statement without duration must yield UNKNOWN duration."""
    mock_json = json.dumps({
        "problemSummary": "Overgrown bushes blocking sidewalk",
        "primaryDomain": "Urban Infrastructure",
        "secondaryDomains": [],
        "subcategory": "Roads",
        "severity": "LOW",
        "severityAssessment": {
            "healthSafetyImpact": "NONE",
            "exposureScope": "LOCAL",
            "vulnerablePopulationExposure": "NONE_IDENTIFIED",
            "geographicExtent": "SINGLE_LOCATION",
            "duration": "UNKNOWN",
            "infrastructureImpact": "LOW",
            "environmentalImpact": "NONE",
            "socialEconomicImpact": "NONE",
            "reversibility": "EASILY_REVERSIBLE"
        },
        "severityEvidence": ["Bushes blocking pedestrian path."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "LOW",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Horticulture"],
        "requiredResources": ["Trimming Tools"],
        "confidence": 0.88,
        "reasoning": "Minor pedestrian obstruction without specified timeframe."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2010",
        title="Overgrown bushes on sidewalk",
        description="Bushes are overgrown on the sidewalk near the park.",
        location=ProblemLocation(district="Chandigarh", state="Punjab")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severityAssessment.duration == DurationEnum.UNKNOWN


@pytest.mark.asyncio
async def test_case_11_explicit_duration():
    """Scenario 11: Explicit duration mentioned in text ("leaking for 3 days") yields ONGOING duration."""
    mock_json = json.dumps({
        "problemSummary": "Water leaking continuously for three days",
        "primaryDomain": "Water Resources",
        "secondaryDomains": [],
        "subcategory": "Leakage",
        "severity": "MEDIUM",
        "severityAssessment": {
            "healthSafetyImpact": "LOW",
            "exposureScope": "LOCAL",
            "vulnerablePopulationExposure": "NONE_IDENTIFIED",
            "geographicExtent": "SINGLE_LOCATION",
            "duration": "ONGOING",
            "infrastructureImpact": "MODERATE",
            "environmentalImpact": "LOW",
            "socialEconomicImpact": "NONE",
            "reversibility": "EASILY_REVERSIBLE"
        },
        "severityEvidence": ["Water leakage has continued for 3 days."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Plumbing"],
        "requiredResources": ["Pipe Repair Parts"],
        "confidence": 0.90,
        "reasoning": "Active leak ongoing for 3 days."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2011",
        title="Water leaking for 3 days",
        description="A public tap has been leaking continuously for three days.",
        location=ProblemLocation(district="Surat", state="Gujarat")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severityAssessment.duration == DurationEnum.ONGOING


@pytest.mark.asyncio
async def test_case_12_severe_problem_with_low_evidence():
    """Scenario 12: High severity problem with incomplete evidence receives lower confidence and review_required status."""
    mock_json = json.dumps({
        "problemSummary": "Unconfirmed toxic chemical fumes near residential zone",
        "primaryDomain": "Environment",
        "secondaryDomains": ["Healthcare"],
        "subcategory": "Pollution",
        "severity": "HIGH",
        "severityAssessment": {
            "healthSafetyImpact": "HIGH",
            "exposureScope": "UNKNOWN",
            "vulnerablePopulationExposure": "UNKNOWN",
            "geographicExtent": "LOCAL_AREA",
            "duration": "UNKNOWN",
            "infrastructureImpact": "UNKNOWN",
            "environmentalImpact": "HIGH",
            "socialEconomicImpact": "UNKNOWN",
            "reversibility": "UNKNOWN"
        },
        "severityEvidence": ["Fumes causing nausea reported near residential area."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Environmental Inspection"],
        "requiredResources": ["Air Quality Sensors"],
        "confidence": 0.62,  # Low confidence due to incomplete evidence
        "reasoning": "Potentially serious chemical hazard but evidence is incomplete."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2012",
        title="Strange chemical fumes",
        description="People feel sick from strange chemical fumes near the boundary wall.",
        location=ProblemLocation(district="Vadodara", state="Gujarat")
    )

    response = await service.classify_problem(inp)
    # Even though severity is HIGH, confidence is 0.62 (< 0.85), so status is REVIEW_REQUIRED
    assert response.status == StatusEnum.REVIEW_REQUIRED
    assert response.classification.severity == SeverityEnum.HIGH
    assert response.classification.confidence == 0.62


@pytest.mark.asyncio
async def test_case_13_high_severity_low_confidence():
    """Scenario 13: Verify high severity with low confidence triggers review_required safeguard."""
    mock_json = json.dumps({
        "problemSummary": "Reported structural crack on overpass",
        "primaryDomain": "Urban Infrastructure",
        "secondaryDomains": [],
        "subcategory": "Public Spaces",
        "severity": "HIGH",
        "severityAssessment": {
            "healthSafetyImpact": "HIGH",
            "exposureScope": "COMMUNITY",
            "vulnerablePopulationExposure": "POSSIBLE",
            "geographicExtent": "SINGLE_LOCATION",
            "duration": "UNKNOWN",
            "infrastructureImpact": "HIGH",
            "environmentalImpact": "NONE",
            "socialEconomicImpact": "MODERATE",
            "reversibility": "RECOVERABLE"
        },
        "severityEvidence": ["Crack reported on flyover pillar."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "MEDIUM",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Structural Engineering"],
        "requiredResources": ["Inspection Equipment"],
        "confidence": 0.70,
        "reasoning": "Overpass crack requires human structural review."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2013",
        title="Flyover crack",
        description="Saw a crack on the pillar of the flyover near railway station.",
        location=ProblemLocation(district="Nagpur", state="Maharashtra")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.REVIEW_REQUIRED
    assert response.classification.severity == SeverityEnum.HIGH


@pytest.mark.asyncio
async def test_case_14_low_severity_problem():
    """Scenario 14: Minor issue should yield LOW severity and LOW impact across factors."""
    mock_json = json.dumps({
        "problemSummary": "Faded paint on street signboard",
        "primaryDomain": "Urban Infrastructure",
        "secondaryDomains": [],
        "subcategory": "Public Spaces",
        "severity": "LOW",
        "severityAssessment": {
            "healthSafetyImpact": "NONE",
            "exposureScope": "LOCAL",
            "vulnerablePopulationExposure": "NONE_IDENTIFIED",
            "geographicExtent": "SINGLE_LOCATION",
            "duration": "LONG_TERM",
            "infrastructureImpact": "LOW",
            "environmentalImpact": "NONE",
            "socialEconomicImpact": "NONE",
            "reversibility": "EASILY_REVERSIBLE"
        },
        "severityEvidence": ["Street sign paint is faded."],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "LOW",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Maintenance"],
        "requiredResources": ["Paint"],
        "confidence": 0.95,
        "reasoning": "Cosmetic signage maintenance."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2014",
        title="Faded street sign",
        description="The name sign for Sector 4 is faded and hard to read.",
        location=ProblemLocation(district="Noida", state="Uttar Pradesh")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severity == SeverityEnum.LOW
    assert response.classification.severityAssessment.healthSafetyImpact == HealthSafetyImpactEnum.NONE


@pytest.mark.asyncio
async def test_case_15_critical_safety_problem():
    """Scenario 15: High-voltage wire hanging low in public park -> CRITICAL healthSafetyImpact and CRITICAL severity."""
    mock_json = json.dumps({
        "problemSummary": "Live high-voltage electric wire hanging in public park",
        "primaryDomain": "Energy",
        "secondaryDomains": ["Healthcare"],
        "subcategory": "Public Lighting",
        "severity": "CRITICAL",
        "severityAssessment": {
            "healthSafetyImpact": "CRITICAL",
            "exposureScope": "COMMUNITY",
            "vulnerablePopulationExposure": "CLEAR",
            "geographicExtent": "LOCAL_AREA",
            "duration": "SHORT_TERM",
            "infrastructureImpact": "HIGH",
            "environmentalImpact": "NONE",
            "socialEconomicImpact": "NONE",
            "reversibility": "EASILY_REVERSIBLE"
        },
        "severityEvidence": [
            "Live high-voltage wire hanging near children's play area in park."
        ],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "CRITICAL",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Electrical Engineering"],
        "requiredResources": ["Utility Repair Van"],
        "confidence": 0.95,
        "reasoning": "Immediate life-threatening electrocution risk in public recreational space."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2015",
        title="Live wire hanging in park",
        description="A live high-voltage electric wire is hanging low near the swings in Children's Park.",
        location=ProblemLocation(district="Delhi", state="Delhi")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severity == SeverityEnum.CRITICAL
    assert response.classification.severityAssessment.healthSafetyImpact == HealthSafetyImpactEnum.CRITICAL


@pytest.mark.asyncio
async def test_case_16_severity_vs_urgency_distinction():
    """Scenario 16: Verify independence of severity and urgency (Case B: HIGH severity, MEDIUM urgency)."""
    mock_json = json.dumps({
        "problemSummary": "Isolated abandoned structure with severe structural damage",
        "primaryDomain": "Urban Infrastructure",
        "secondaryDomains": [],
        "subcategory": "Public Spaces",
        "severity": "HIGH",
        "severityAssessment": {
            "healthSafetyImpact": "HIGH",
            "exposureScope": "LOCAL",
            "vulnerablePopulationExposure": "NONE_IDENTIFIED",
            "geographicExtent": "SINGLE_LOCATION",
            "duration": "LONG_TERM",
            "infrastructureImpact": "HIGH",
            "environmentalImpact": "NONE",
            "socialEconomicImpact": "NONE",
            "reversibility": "RECOVERABLE"
        },
        "severityEvidence": [
            "Large abandoned structure has major structural wall cracks.",
            "Site is fenced off and currently isolated from immediate foot traffic."
        ],
        "peopleAffected": {
            "value": None,
            "unit": None,
            "source": "NOT_PROVIDED"
        },
        "urgency": "MEDIUM",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Demolition", "Structural Engineering"],
        "requiredResources": ["Demolition Equipment"],
        "confidence": 0.91,
        "reasoning": "High severity harm potential if collapsed, but isolated site lowers immediate urgency."
    })

    service = ClassifierService(llm_provider=MockLLMProvider(response_text=mock_json))
    inp = ProblemClassificationInput(
        problemId="P2016",
        title="Damaged abandoned warehouse",
        description="A large abandoned structure has serious structural damage but is currently fenced and isolated.",
        location=ProblemLocation(district="Ahmedabad", state="Gujarat")
    )

    response = await service.classify_problem(inp)
    assert response.status == StatusEnum.CLASSIFIED
    assert response.classification.severity == SeverityEnum.HIGH
    assert response.classification.urgency == UrgencyEnum.MEDIUM
