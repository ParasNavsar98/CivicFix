import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schemas.input import ProblemClassificationInput, ProblemLocation
from app.services.classifier import ClassifierService

cases = [
    {
        "id": "CASE-1",
        "title": "Unsafe school toilets causing students to miss classes",
        "description": "The government school has severely damaged and unusable toilets. Students are frequently unable to attend classes because there are no functional sanitation facilities. The problem creates both a sanitation failure and a direct education access problem."
    },
    {
        "id": "CASE-2",
        "title": "Garbage burning near school",
        "description": "People are regularly burning garbage near the government school. Thick smoke enters the classrooms and students are exposed to the smoke during school hours."
    },
    {
        "id": "CASE-3",
        "title": "Broken school toilets",
        "description": "The government school toilets are damaged and unusable. The facilities require repair."
    },
    {
        "id": "CASE-4",
        "title": "Poor school sanitation causes students to miss classes",
        "description": "The school toilets are unusable because of severe sanitation problems. Students are repeatedly unable to attend classes because they cannot access functional sanitation facilities."
    },
    {
        "id": "CASE-5",
        "title": "Low crop prices and lack of irrigation",
        "description": "Farmers are simultaneously facing inadequate irrigation and difficulty accessing markets, resulting in crop losses and poor income."
    }
]

async def run():
    service = ClassifierService()
    for c in cases:
        inp = ProblemClassificationInput(
            problemId=c["id"],
            title=c["title"],
            description=c["description"],
            location=ProblemLocation(district="Ranchi", state="Jharkhand")
        )
        resp = await service.classify_problem(inp)
        cls = resp.classification
        if cls:
            print(f"{c['id']}: primary={cls.primaryDomain}, sub={cls.subcategory}, secondary={cls.secondaryDomains}")
        else:
            print(f"{c['id']}: FAILED error={resp.error}")

if __name__ == "__main__":
    asyncio.run(run())
