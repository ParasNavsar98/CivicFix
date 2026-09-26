# ============================================================
# CivicFix - Complete Local Development Launcher
# ============================================================

$ErrorActionPreference = "Continue"

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

$ROOT = "D:\CivicFix"

$CLASSIFICATION_DIR = "$ROOT\classification-engine"
$DUPLICATE_DIR      = "$ROOT\duplicate-detection"
$BACKEND_DIR        = "$ROOT\backend"
$FRONTEND_DIR       = "$ROOT\testing-console"

$CLASSIFICATION_PORT = 8000
$DUPLICATE_PORT      = 8001
$BACKEND_PORT        = 8002
$FRONTEND_PORT       = 5173

$OLLAMA_MODEL = "gemma3:4b"

# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

function Write-Info($message) {
    Write-Host "[CivicFix] $message" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "[OK] $message" -ForegroundColor Green
}

function Write-WarningMsg($message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-ErrorMsg($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

function Test-Directory($path, $name) {
    if (!(Test-Path $path)) {
        Write-ErrorMsg "$name directory not found:"
        Write-Host $path
        return $false
    }

    Write-Success "$name found"
    return $true
}

function Start-CivicFixTerminal {
    param(
        [string]$Title,
        [string]$WorkingDirectory,
        [string]$Command
    )

    Write-Info "Starting $Title..."

    Start-Process powershell.exe `
        -ArgumentList "-NoExit", "-Command", `
        "Set-Location '$WorkingDirectory'; `$Host.UI.RawUI.WindowTitle='$Title'; $Command"

    Start-Sleep -Seconds 2
}

# ------------------------------------------------------------
# START
# ------------------------------------------------------------

Clear-Host

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "                 CIVICFIX LOCAL SYSTEM" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

Write-Info "Project root: $ROOT"
Write-Host ""

# ------------------------------------------------------------
# CHECK PROJECT DIRECTORIES
# ------------------------------------------------------------

if (!(Test-Directory $ROOT "CivicFix root")) {
    exit 1
}

if (!(Test-Directory $CLASSIFICATION_DIR "Classification Engine")) {
    exit 1
}

if (!(Test-Directory $DUPLICATE_DIR "Duplicate Detection Engine")) {
    exit 1
}

if (!(Test-Directory $BACKEND_DIR "Backend")) {
    exit 1
}

if (!(Test-Directory $FRONTEND_DIR "Testing Console")) {
    exit 1
}

Write-Host ""

# ------------------------------------------------------------
# CHECK PYTHON
# ------------------------------------------------------------

Write-Info "Checking Python..."

try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python detected: $pythonVersion"
}
catch {
    Write-ErrorMsg "Python was not found in PATH."
    exit 1
}

# ------------------------------------------------------------
# CHECK NODE
# ------------------------------------------------------------

Write-Info "Checking Node.js..."

try {
    $nodeVersion = node --version 2>&1
    Write-Success "Node detected: $nodeVersion"
}
catch {
    Write-ErrorMsg "Node.js was not found in PATH."
    exit 1
}

# ------------------------------------------------------------
# CHECK OLLAMA
# ------------------------------------------------------------

Write-Info "Checking Ollama..."

try {
    $ollamaVersion = ollama --version 2>&1
    Write-Success "Ollama detected: $ollamaVersion"
}
catch {
    Write-ErrorMsg "Ollama was not found."
    Write-Host "Install Ollama first."
    exit 1
}

# ------------------------------------------------------------
# CHECK OLLAMA MODEL
# ------------------------------------------------------------

Write-Info "Checking Ollama model: $OLLAMA_MODEL"

$models = ollama list 2>&1

if ($models -match [regex]::Escape($OLLAMA_MODEL)) {
    Write-Success "$OLLAMA_MODEL is installed"
}
else {
    Write-WarningMsg "$OLLAMA_MODEL was not found."
    Write-Info "Pulling model..."

    ollama pull $OLLAMA_MODEL

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to pull $OLLAMA_MODEL"
        exit 1
    }

    Write-Success "$OLLAMA_MODEL installed"
}

# ------------------------------------------------------------
# CHECK / START OLLAMA
# ------------------------------------------------------------

Write-Info "Checking Ollama API..."

try {
    $ollamaHealth = Invoke-WebRequest `
        -Uri "http://localhost:11434/api/tags" `
        -UseBasicParsing `
        -TimeoutSec 3

    Write-Success "Ollama API already running"
}
catch {

    Write-WarningMsg "Ollama API is not running."

    Write-Info "Starting Ollama..."

    Start-Process powershell.exe `
        -ArgumentList "-NoExit", "-Command", `
        "`$Host.UI.RawUI.WindowTitle='CivicFix - Ollama'; ollama serve"

    Start-Sleep -Seconds 5

    try {
        Invoke-WebRequest `
            -Uri "http://localhost:11434/api/tags" `
            -UseBasicParsing `
            -TimeoutSec 5 | Out-Null

        Write-Success "Ollama API started"
    }
    catch {
        Write-ErrorMsg "Could not start Ollama API."
        exit 1
    }
}

# ------------------------------------------------------------
# CHECK FRONTEND DEPENDENCIES
# ------------------------------------------------------------

Write-Info "Checking frontend dependencies..."

if (!(Test-Path "$FRONTEND_DIR\node_modules")) {

    Write-WarningMsg "node_modules not found."
    Write-Info "Installing frontend dependencies..."

    Start-Process powershell.exe `
        -Wait `
        -ArgumentList "-NoExit", "-Command", `
        "Set-Location '$FRONTEND_DIR'; npm install"

    Write-Success "Frontend dependencies installed"
}
else {
    Write-Success "Frontend dependencies already installed"
}

# ------------------------------------------------------------
# START CLASSIFICATION ENGINE
# ------------------------------------------------------------

Start-CivicFixTerminal `
    -Title "CivicFix - Classification Engine :8000" `
    -WorkingDirectory $CLASSIFICATION_DIR `
    -Command "python -m uvicorn app.main:app --host 0.0.0.0 --port $CLASSIFICATION_PORT"

# ------------------------------------------------------------
# START DUPLICATE DETECTION ENGINE
# ------------------------------------------------------------

Start-CivicFixTerminal `
    -Title "CivicFix - Duplicate Detection :8001" `
    -WorkingDirectory $DUPLICATE_DIR `
    -Command "python -m uvicorn app.main:app --host 0.0.0.0 --port $DUPLICATE_PORT"

# ------------------------------------------------------------
# START MAIN BACKEND
# ------------------------------------------------------------

Start-CivicFixTerminal `
    -Title "CivicFix - Main Backend :8002" `
    -WorkingDirectory $BACKEND_DIR `
    -Command "`$env:PYTHONPATH='$BACKEND_DIR'; python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT"

# ------------------------------------------------------------
# START TESTING CONSOLE
# ------------------------------------------------------------

Start-CivicFixTerminal `
    -Title "CivicFix - Testing Console :5173" `
    -WorkingDirectory $FRONTEND_DIR `
    -Command "npm run dev -- --host 0.0.0.0"

# ------------------------------------------------------------
# WAIT FOR SERVICES
# ------------------------------------------------------------

Write-Host ""
Write-Info "Waiting for services to start..."

Start-Sleep -Seconds 8

# ------------------------------------------------------------
# HEALTH CHECKS
# ------------------------------------------------------------

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                   SERVICE HEALTH CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

function Check-Service($name, $url) {

    try {

        $response = Invoke-WebRequest `
            -Uri $url `
            -UseBasicParsing `
            -TimeoutSec 5

        if ($response.StatusCode -eq 200) {
            Write-Success "$name -> ONLINE"
            return $true
        }

    }
    catch {
        Write-WarningMsg "$name -> NOT READY"
        return $false
    }

    return $false
}

Check-Service "Ollama" "http://localhost:11434/api/tags"

Check-Service `
    "Classification Engine" `
    "http://localhost:$CLASSIFICATION_PORT/health"

Check-Service `
    "Duplicate Detection" `
    "http://localhost:$DUPLICATE_PORT/health"

Check-Service `
    "Main Backend" `
    "http://localhost:$BACKEND_PORT/health"

# ------------------------------------------------------------
# FINAL INFORMATION
# ------------------------------------------------------------

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                 CIVICFIX IS STARTING" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host ""
Write-Host "  Ollama                  http://localhost:11434"
Write-Host "  Classification Engine   http://localhost:8000"
Write-Host "  Duplicate Detection     http://localhost:8001"
Write-Host "  Main Backend            http://localhost:8002"
Write-Host "  Testing Console         http://localhost:5173"

Write-Host ""
Write-Host "API Documentation:" -ForegroundColor White
Write-Host ""
Write-Host "  Classification Swagger  http://localhost:8000/docs"
Write-Host "  Duplicate Swagger       http://localhost:8001/docs"
Write-Host "  Backend Swagger         http://localhost:8002/docs"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Write-Info "Opening Testing Console..."

Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "CivicFix startup complete." -ForegroundColor Green
Write-Host "Keep the opened terminals running."
Write-Host ""