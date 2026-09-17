import re
from app.schemas.input import ProblemClassificationInput, ProblemLocation


def normalize_text(text: str) -> str:
    """Normalize text by trimming and collapsing multiple spaces while keeping sentence integrity."""
    if not text:
        return ""
    # Strip leading and trailing whitespace
    text = text.strip()
    # Normalize internal spaces while preserving newline breaks cleanly
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text


def sanitize_and_preprocess(input_data: ProblemClassificationInput) -> ProblemClassificationInput:
    """Preprocess citizen input without altering semantic meaning or removing stop words."""
    cleaned_problem_id = normalize_text(input_data.problemId)
    cleaned_title = normalize_text(input_data.title)
    cleaned_description = normalize_text(input_data.description)
    cleaned_district = normalize_text(input_data.location.district)
    cleaned_state = normalize_text(input_data.location.state)

    if not cleaned_title or not cleaned_description:
        raise ValueError("Title and description cannot be empty after preprocessing.")

    cleaned_location = ProblemLocation(
        district=cleaned_district,
        state=cleaned_state,
        latitude=input_data.location.latitude,
        longitude=input_data.location.longitude,
    )

    return ProblemClassificationInput(
        problemId=cleaned_problem_id,
        title=cleaned_title,
        description=cleaned_description,
        location=cleaned_location,
    )
