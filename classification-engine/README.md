# Societal Innovation Portal - Standalone AI Classification Engine

The **AI Classification Engine** is a production-quality, modular Python microservice built with **FastAPI**, **Pydantic v2**, and **Ollama (Gemma 3 4B)** as its sole local LLM backend. It receives unstructured societal problem submissions from citizens and produces structured, standardized AI classifications.

---

## 1. Project Purpose
Citizens report societal problems in unstructured text (e.g. "Garbage burning near school", "Water pipeline leakage"). The engine analyzes the text, assigns it to a controlled 12-domain taxonomy, determines severity and urgency, identifies required expertise/resources, assesses whether research or government action is needed, and calculates an AI confidence estimate.

The engine is **AI-assisted**: it recommends classifications and flags low-confidence or ambiguous submissions for human review (`review_required`), ensuring AI never makes irreversible real-world decisions automatically.

---

## 2. High-Level Architecture
```text
Citizen Problem
      │
      ▼
FastAPI /classify
      │
      ▼
Input Validation (Pydantic v2)
      │
      ▼
Text Preprocessing (Normalization)
      │
      ▼
Taxonomy Loading (12 Controlled Domains)
      │
      ▼
Classification Prompt Construction
      │
      ▼
LLMProvider (Ollama Local API / Gemma 3 4B)
      │
      ▼
Pydantic Schema & Business Rule Validation
      │
      ▼
Confidence & Safeguards Evaluation Engine
      ├──────────────────────────────┐
      ▼                              ▼
High Confidence (>= 0.85)     Low Confidence (< 0.85)
      │                              │
      ▼                              ▼
   classified                  review_required
      └──────────────┬───────────────┘
                     ▼
             Final API Response
```

---

## 3. Technology Stack
- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Data Validation**: Pydantic v2 & Pydantic-Settings
- **LLM Backend**: Ollama with **Gemma 3 4B** (`gemma3:4b` running locally)
- **HTTP Client**: `httpx` (Async timeout & exponential backoff retries)
- **Environment Management**: `python-dotenv`
- **Testing**: `pytest`, `pytest-asyncio`

---

## 4. Folder Structure
```text
classification-engine/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application & HTTP endpoints
│   ├── config.py                # Centralized Pydantic configuration
│   │
│   ├── schemas/                 # Pydantic data contracts
│   │   ├── __init__.py
│   │   ├── input.py             # Citizen input validation model
│   │   └── classification.py    # Output result and response schemas
│   │
│   ├── services/                # Core business logic
│   │   ├── __init__.py
│   │   ├── preprocessor.py     # Input sanitization & normalization
│   │   ├── classifier.py       # Orchestration & taxonomy validation
│   │   └── confidence.py       # Threshold confidence evaluation engine
│   │
│   ├── ai/                      # LLM Provider integration
│   │   ├── __init__.py
│   │   ├── provider.py         # Abstract LLM provider interface
│   │   ├── ollama.py           # Ollama local API provider
│   │   └── prompts.py          # Dynamic prompt generator for Gemma 3 4B
│   │
│   └── taxonomy/                # Isolated taxonomy definition
│       ├── __init__.py
│       └── taxonomy.py         # 12 controlled primary domains & subcategories
│
├── tests/                       # Complete automated testing suite
│   ├── __init__.py
│   ├── evaluation_dataset.json # 50-item ground truth test dataset
│   ├── test_api.py
│   ├── test_classifier.py
│   ├── test_confidence.py
│   ├── test_ollama.py
│   ├── test_precision_and_metrics.py
│   ├── test_schemas.py
│   ├── test_security.py
│   └── test_taxonomy.py
│
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git ignore settings
├── requirements.txt             # Python dependencies
└── README.md                    # Service documentation
```

---

## 5. Ollama & Gemma 3 4B Setup

### Step 1: Install Ollama
Download and install Ollama on Windows from [https://ollama.com](https://ollama.com).

Verify installation in PowerShell:
```powershell
ollama --version
```

### Step 2: Pull the Gemma 3 4B Model
Pull the required local model:
```powershell
ollama pull gemma3:4b
```

### Step 3: Verify Installed Models
List local models to confirm `gemma3:4b` is present:
```powershell
ollama list
```

### Step 4: Test Model Interactively (Optional)
```powershell
ollama run gemma3:4b
```

---

## 6. Project Setup & Installation

### Virtual Environment Setup
```bash
# Navigate into the project folder
cd classification-engine

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

---

## 7. Environment Variables & Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Default `.env` configuration (Local Ollama mode - No API keys required):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b

LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=3

AI_HIGH_CONFIDENCE_THRESHOLD=0.85
AI_REVIEW_THRESHOLD=0.60
```

---

## 8. Running the FastAPI Server
Start the development server with Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger API Docs are available at: `http://localhost:8000/docs`.

---

## 9. API Endpoints & Usage

### Health Check
- **GET `/health`**
- **Response**: `{"status": "healthy"}`
> **Note**: `/health` indicates application service status and functions cleanly even if Ollama is temporarily offline.

### Classify Problem
- **POST `/classify`**
- **Content-Type**: `application/json`

#### Example Request (`PowerShell / Invoke-RestMethod`)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/classify" -Method Post -ContentType "application/json" -Body '{
  "problemId": "P1001",
  "title": "Garbage burning near school",
  "description": "People dump garbage near our school and burn it every evening. Harmful smoke and gases affect nearby residents.",
  "location": {
    "district": "Ranchi",
    "state": "Jharkhand",
    "latitude": 23.3441,
    "longitude": 85.3096
  }
}'
```

#### Successful Classification Response (`status: "classified"`)
```json
{
  "problemId": "P1001",
  "status": "classified",
  "classification": {
    "problemSummary": "Open garbage burning near school causing smoke pollution",
    "primaryDomain": "Environment",
    "secondaryDomains": ["Sanitation", "Healthcare"],
    "subcategory": "Pollution",
    "severity": "HIGH",
    "urgency": "HIGH",
    "researchRequired": false,
    "governmentActionPossible": true,
    "requiredExpertise": [
      "Waste Management",
      "Environmental Engineering"
    ],
    "requiredResources": [
      "Waste collection vehicles",
      "Pollution monitoring"
    ],
    "confidence": 0.91,
    "reasoning": "Outdoor burning of waste near a school creates acute environmental pollution."
  },
  "error": null
}
```

#### Low Confidence Response (`status: "review_required"`)
```json
{
  "problemId": "P1002",
  "status": "review_required",
  "classification": {
    "problemSummary": "Unclear village problem",
    "primaryDomain": "Other",
    "secondaryDomains": [],
    "subcategory": "Unclassified",
    "severity": "LOW",
    "urgency": "LOW",
    "researchRequired": false,
    "governmentActionPossible": false,
    "requiredExpertise": [],
    "requiredResources": [],
    "confidence": 0.40,
    "reasoning": "Input lacks actionable details."
  },
  "error": null
}
```

#### Controlled Provider Error Response (`status: "failed"`)
```json
{
  "problemId": "P1003",
  "status": "failed",
  "classification": null,
  "error": {
    "errorCode": "AI_PROVIDER_UNAVAILABLE",
    "message": "Unable to connect to Ollama. Make sure Ollama is running at http://localhost:11434."
  }
}
```

---

## 10. Troubleshooting

### Ollama Not Running (`AI_PROVIDER_UNAVAILABLE`)
If `/classify` returns `AI_PROVIDER_UNAVAILABLE`:
1. Check if Ollama is running in system tray or service manager.
2. Start Ollama service or launch `ollama app` / `ollama serve`.
3. Verify access at `http://localhost:11434`.

### Model Missing (`AI_MODEL_NOT_FOUND`)
If `/classify` returns `AI_MODEL_NOT_FOUND`:
1. Check installed models with `ollama list`.
2. Download model using `ollama pull gemma3:4b`.

---

## 11. Testing
Run the complete automated test suite using `pytest`:
```bash
pytest -v
```
All unit tests mock external LLM/Ollama network calls to run fast and deterministically offline.

---

## 12. Future Extension Points
Designed for seamless integration into larger platforms:
1. Multilingual input translation
2. Image & Video multi-modal analysis
3. Vector embeddings & duplicate problem detection
4. Custom fine-tuned ML model evaluation
5. Human feedback & active learning loops
