import json
import logging
import time
from typing import Optional

from app.config import settings
from app.ai.provider import LLMProvider, LLMProviderException
from app.ai.ollama import OllamaProvider
from app.ai.prompts import build_classification_prompt
from app.schemas.input import ProblemClassificationInput
from app.schemas.classification import (
    ClassificationResult,
    ClassificationResponse,
    StatusEnum,
    ErrorDetails,
)
from app.services.preprocessor import sanitize_and_preprocess
from app.services.confidence import evaluate_confidence
from app.taxonomy.taxonomy import is_valid_domain, is_valid_subcategory

logger = logging.getLogger(__name__)


class TaxonomyValidationError(Exception):
    """Raised when LLM output violates controlled taxonomy constraints."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ClassifierService:
    """Core classification engine orchestrator."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or OllamaProvider()

    def validate_taxonomy_rules(self, result: ClassificationResult) -> None:
        """Enforce strict business and taxonomy validation on LLM classification output."""
        if not is_valid_domain(result.primaryDomain):
            raise TaxonomyValidationError(
                f"Invalid primary domain '{result.primaryDomain}'. Must be one of controlled taxonomy domains."
            )

        if not is_valid_subcategory(result.primaryDomain, result.subcategory):
            raise TaxonomyValidationError(
                f"Invalid subcategory '{result.subcategory}' for domain '{result.primaryDomain}'."
            )

        for sec_domain in result.secondaryDomains:
            if not is_valid_domain(sec_domain):
                raise TaxonomyValidationError(
                    f"Invalid secondary domain '{sec_domain}'. Must be a valid primary domain from controlled taxonomy."
                )

    def is_evidence_sufficient(self, input_data: ProblemClassificationInput) -> bool:
        """Evaluate whether citizen problem submission provides sufficient actionable detail."""
        desc = input_data.description.strip()
        title = input_data.title.strip()
        words = desc.split()

        # Very short or minimal descriptions
        if len(words) < 5 or len(desc) < 20:
            return False

        # Generic vague phrases lacking specific domain context
        vague_phrases = [
            "problem in my village",
            "everything is bad",
            "nobody is helping us",
            "system is not working",
            "things are getting worse",
            "serious problem here",
            "needs help",
        ]
        lowered_desc = desc.lower()
        if any(phrase in lowered_desc for phrase in vague_phrases) and len(words) < 12:
            return False

        return True

    def detect_ambiguity(
        self, result: ClassificationResult, evidence_sufficient: bool
    ) -> bool:
        """Detect ambiguous or uncertain classification outputs."""
        if not evidence_sufficient:
            return True

        # Unclassified fallback mapping
        if result.primaryDomain == "Other" and result.subcategory == "Unclassified":
            return True

        # Confidence below high confidence threshold
        if result.confidence < settings.AI_HIGH_CONFIDENCE_THRESHOLD:
            return True

        return False

    async def classify_problem(
        self, input_data: ProblemClassificationInput
    ) -> ClassificationResponse:
        """Main classification pipeline."""
        start_time = time.time()
        problem_id = input_data.problemId

        logger.info("[%s] Classification pipeline started", problem_id)

        try:
            # 1. Preprocessing
            processed_input = sanitize_and_preprocess(input_data)

            # 2. Prompt Construction
            prompt = build_classification_prompt(processed_input)

            # 3. LLM Provider Execution (Pass structured output schema)
            schema = ClassificationResult.model_json_schema()
            raw_response = await self.llm_provider.classify(prompt, response_schema=schema)

            # 4. JSON Parsing
            try:
                # Strip markdown fence blocks if present in response
                cleaned_response = raw_response.strip()
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response.strip("`")
                    if cleaned_response.startswith("json"):
                        cleaned_response = cleaned_response[4:].strip()
                
                parsed_json = json.loads(cleaned_response)
            except json.JSONDecodeError as err:
                logger.error("[%s] Invalid JSON returned by LLM: %s", problem_id, str(err))
                return ClassificationResponse(
                    problemId=problem_id,
                    status=StatusEnum.FAILED,
                    error=ErrorDetails(
                        errorCode="AI_INVALID_JSON",
                        message="AI provider response could not be parsed as JSON.",
                    ),
                )

            # 5. Pydantic Output Schema Validation
            try:
                classification_result = ClassificationResult.model_validate(parsed_json)
            except Exception as err:
                logger.error("[%s] ClassificationResult Pydantic validation failed: %s", problem_id, str(err))
                return ClassificationResponse(
                    problemId=problem_id,
                    status=StatusEnum.FAILED,
                    error=ErrorDetails(
                        errorCode="AI_VALIDATION_ERROR",
                        message=f"AI output failed schema validation: {str(err)}",
                    ),
                )

            # 6. Business & Taxonomy Validation
            try:
                self.validate_taxonomy_rules(classification_result)
            except TaxonomyValidationError as err:
                logger.error("[%s] Taxonomy validation failed: %s", problem_id, err.message)
                return ClassificationResponse(
                    problemId=problem_id,
                    status=StatusEnum.FAILED,
                    error=ErrorDetails(
                        errorCode="INVALID_TAXONOMY_CATEGORY",
                        message=err.message,
                    ),
                )

            # 7. Evidence Sufficiency & Ambiguity Safeguards
            evidence_sufficient = self.is_evidence_sufficient(processed_input)
            ambiguity_detected = self.detect_ambiguity(classification_result, evidence_sufficient)

            # 8. Confidence Evaluation
            status = evaluate_confidence(
                confidence=classification_result.confidence,
                evidence_sufficient=evidence_sufficient,
                ambiguity_detected=ambiguity_detected,
            )

            elapsed = time.time() - start_time
            logger.info(
                "[%s] Classification complete in %.2fs. Confidence: %.2f (Sufficient: %s, Ambiguous: %s) -> Status: %s",
                problem_id,
                elapsed,
                classification_result.confidence,
                evidence_sufficient,
                ambiguity_detected,
                status.value,
            )

            return ClassificationResponse(
                problemId=problem_id,
                status=status,
                classification=classification_result,
            )

        except LLMProviderException as err:
            logger.error("[%s] LLM Provider error (%s): %s", problem_id, err.error_code, err.message)
            return ClassificationResponse(
                problemId=problem_id,
                status=StatusEnum.FAILED,
                error=ErrorDetails(
                    errorCode=err.error_code,
                    message=err.message,
                ),
            )
        except Exception as err:
            logger.exception("[%s] Unexpected classification failure: %s", problem_id, str(err))
            return ClassificationResponse(
                problemId=problem_id,
                status=StatusEnum.FAILED,
                error=ErrorDetails(
                    errorCode="INTERNAL_ERROR",
                    message="An unexpected internal server error occurred.",
                ),
            )
