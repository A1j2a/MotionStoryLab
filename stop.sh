#!/usr/bin/env bash
# ==============================================================================
# AI Kids Video Studio - Graceful Shutdown Script
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="${SCRIPT_DIR}/logs/pids"

echo "Stopping AI Kids Video Studio services..."

stop_pid_file() {
    local service_name="$1"
    local pid_file="${PID_DIR}/${service_name}.pid"

    if [ -f "${pid_file}" ]; then
        local pid
        pid=$(cat "${pid_file}")
        if kill -0 "${pid}" >/dev/null 2>&1; then
            echo "Stopping ${service_name} (PID: ${pid})..."
            kill "${pid}" 2>/dev/null || true
            sleep 1
            if kill -0 "${pid}" >/dev/null 2>&1; then
                kill -9 "${pid}" 2>/dev/null || true
            fi
            echo "  ✓ Stopped ${service_name}"
        else
            echo "  ${service_name} was not running."
        fi
        rm -f "${pid_file}"
    fi
}

stop_pid_file "backend"
stop_pid_file "frontend"
stop_pid_file "ollama"
stop_pid_file "tts"
stop_pid_file "comfyui"
stop_pid_file "n8n"

# Clean lingering processes on ports
for PORT in 8000 3000 11434 8880 8188 5678; do
    PIDS=$(lsof -ti :${PORT} 2>/dev/null || true)
    if [ -n "${PIDS}" ]; then
        # shellcheck disable=SC2086
        kill -9 ${PIDS} >/dev/null 2>&1 || true
    fi
done

echo "All studio AI services stopped cleanly."
