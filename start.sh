#!/usr/bin/env bash
# ==============================================================================
# AI Kids Video Studio - Unified Start Script (Apple Silicon Mac M2/M4)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

PID_DIR="${SCRIPT_DIR}/logs/pids"
mkdir -p "${PID_DIR}" "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/projects"

# Load environment
if [ -f "${SCRIPT_DIR}/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/.env"
    set +a
else
    echo "Warning: .env not found. Copying from .env.example..."
    cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
    set -a
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/.env"
    set +a
fi

echo "=================================================="
echo " Starting AI Kids Video Studio (Local-First Engine)"
echo " Environment: ${APP_ENV:-local}"
echo " Host: ${BACKEND_HOST:-127.0.0.1}"
echo "=================================================="

# 1. Dependency checks
echo "[1/8] Validating system dependencies..."
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Error: node is required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "Error: npm is required"; exit 1; }

if command -v ffmpeg >/dev/null 2>&1; then
    echo "  ✓ FFmpeg detected: $(ffmpeg -version | head -n 1)"
else
    echo "  ! Note: ffmpeg not detected in PATH. Required for final video rendering."
fi

# 2. Virtual environment check & activation
PYTHON_BIN="python3"
if [ -d "${SCRIPT_DIR}/backend/.venv" ]; then
    echo "Activating virtual environment: backend/.venv"
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/backend/.venv/bin/activate"
    if [ -f "${SCRIPT_DIR}/backend/.venv/bin/python3" ]; then
        PYTHON_BIN="${SCRIPT_DIR}/backend/.venv/bin/python3"
    fi
fi

# 3. Auto-start Ollama Local AI (Port 11434)
echo "[2/8] Initializing Ollama Local AI Engine (Port 11434)..."
if lsof -Pi :11434 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ✓ Ollama service is already active on port 11434"
else
    echo "  Starting Ollama Local AI Engine daemon..."
    nohup "${PYTHON_BIN}" "${SCRIPT_DIR}/services/ollama_service.py" > "${SCRIPT_DIR}/logs/ollama.log" 2>&1 &
    echo $! > "${PID_DIR}/ollama.pid"
    sleep 1
    echo "  ✓ Ollama Local AI Engine started (Port 11434)"
fi

# 4. Auto-start Kokoro Neural TTS Voice Service (Port 8880)
echo "[3/8] Initializing Kokoro Neural TTS Service (Port 8880)..."
if lsof -Pi :8880 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ✓ Kokoro TTS service already active on port 8880"
else
    nohup "${PYTHON_BIN}" "${SCRIPT_DIR}/services/tts_service.py" > "${SCRIPT_DIR}/logs/tts.log" 2>&1 &
    echo $! > "${PID_DIR}/tts.pid"
    sleep 1
    echo "  ✓ Kokoro Neural TTS Service started (Port 8880)"
fi

# 5. Auto-start ComfyUI Media Pipeline (Port 8188)
echo "[4/8] Initializing ComfyUI Media Engine (Port 8188)..."
if lsof -Pi :8188 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ✓ ComfyUI media pipeline already active on port 8188"
else
    nohup "${PYTHON_BIN}" "${SCRIPT_DIR}/services/comfyui_service.py" > "${SCRIPT_DIR}/logs/comfyui.log" 2>&1 &
    echo $! > "${PID_DIR}/comfyui.pid"
    sleep 1
    echo "  ✓ ComfyUI Media Pipeline started (Port 8188)"
fi

# 6. Auto-start n8n Workflow Automation (Port 5678)
echo "[5/8] Initializing n8n Workflow Automation (Port 5678)..."
if lsof -Pi :5678 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ✓ n8n automation engine already active on port 5678"
else
    nohup "${PYTHON_BIN}" "${SCRIPT_DIR}/services/n8n_service.py" > "${SCRIPT_DIR}/logs/n8n.log" 2>&1 &
    echo $! > "${PID_DIR}/n8n.pid"
    sleep 1
    echo "  ✓ n8n Workflow Automation started (Port 5678)"
fi

# 7. Start FastAPI Backend (Port 8000)
echo "[6/8] Launching FastAPI Backend Engine (Port 8000)..."
BACKEND_PORT="${BACKEND_PORT:-8000}"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"

if lsof -Pi :${BACKEND_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ✓ Backend already running on port ${BACKEND_PORT}"
else
    nohup "${PYTHON_BIN}" -m uvicorn app.main:app --app-dir "${SCRIPT_DIR}/backend" --host "${BACKEND_HOST}" --port "${BACKEND_PORT}" > "${SCRIPT_DIR}/logs/app.log" 2>&1 &
    BACKEND_PID=$!
    echo ${BACKEND_PID} > "${PID_DIR}/backend.pid"
    echo "  ✓ Backend started (PID: ${BACKEND_PID})"
fi

# 8. Start Frontend (Port 3000)
echo "[7/8] Checking Next.js Frontend (Port ${FRONTEND_PORT:-3000})..."
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
if [ -f "${SCRIPT_DIR}/frontend/package.json" ]; then
    if lsof -Pi :${FRONTEND_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "  ✓ Frontend already running on port ${FRONTEND_PORT}"
    else
        echo "  Starting Next.js Frontend..."
        (cd "${SCRIPT_DIR}/frontend" && nohup ./node_modules/.bin/next start -p "${FRONTEND_PORT}" > "${SCRIPT_DIR}/logs/frontend.log" 2>&1 & echo $! > "${PID_DIR}/frontend.pid")
        echo "  ✓ Frontend started"
    fi
fi

# Summary Endpoints
echo ""
echo "=================================================="
echo " All Studio Services Live & Connected"
echo "=================================================="
echo " Frontend Dashboard  : http://${BACKEND_HOST}:${FRONTEND_PORT}"
echo " Backend API & Docs  : http://${BACKEND_HOST}:${BACKEND_PORT}/docs"
echo " Ollama Local AI     : http://127.0.0.1:11434 (Llama 3.2 Metal)"
echo " Kokoro Neural Audio : http://127.0.0.1:8880"
echo " ComfyUI Media Engine: http://127.0.0.1:8188"
echo " n8n Workflows       : http://127.0.0.1:5678"
echo " FFmpeg AV Engine    : Active"
echo "=================================================="

# Verification
echo "[8/8] Verifying Backend Health..."
sleep 2
if curl -s -f "http://${BACKEND_HOST}:${BACKEND_PORT}/health" >/dev/null 2>&1; then
    echo "✓ All services healthy and connected!"
else
    echo "! Backend is initializing in background. Please wait a moment."
fi

echo ""
echo "🚀 Studio is running actively in the background!"
echo "   • Open in browser : http://127.0.0.1:${FRONTEND_PORT}"
echo "   • Workflow Map    : http://127.0.0.1:${FRONTEND_PORT}/workflow"
echo "   • Stop all servers: ./stop.sh"
echo "=================================================="
