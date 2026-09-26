"""
Text preprocessing and sanitization utilities.
Source: classification-engine/app/services/preprocessor.py
"""
import re
from app.schemas.common import ProblemLocation
from app.schemas.classification import ProblemClassificationInput


def sanitize_text(text: str) -> str:
    """Clean and normalize raw citizen input text string."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text


def sanitize_and_preprocess(input_data: ProblemClassificationInput) -> ProblemClassificationInput:
    """Preprocess and sanitize all text fields of citizen submission."""
    cleaned_title = sanitize_text(input_data.title)
    cleaned_description = sanitize_text(input_data.description)
    cleaned_district = sanitize_text(input_data.location.district)
    cleaned_state = sanitize_text(input_data.location.state)

    if not cleaned_title or not cleaned_description:
        raise ValueError("Title and description cannot be empty after preprocessing.")

    cleaned_location = ProblemLocation(
        district=cleaned_district,
        state=cleaned_state,
        latitude=input_data.location.latitude,
        longitude=input_data.location.longitude,
    )

    return ProblemClassificationInput(
        problemId=input_data.problemId.strip(),
        title=cleaned_title,
        description=cleaned_description,
        location=cleaned_location,
    )
