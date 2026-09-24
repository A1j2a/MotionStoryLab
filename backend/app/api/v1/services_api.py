import os
import signal
import socket
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

from app.core.config import settings, BASE_DIR

logger = logging.getLogger("studio.api.services")

router = APIRouter(prefix="/services", tags=["services"])

SERVICES_META = {
    "ollama": {
        "name": "Ollama Local AI",
        "port": 11434,
        "script": "services/ollama_service.py",
        "log": "logs/ollama.log",
        "pid_file": "logs/pids/ollama.pid",
        "desc": "Local LLM Inference Engine",
    },
    "comfyui": {
        "name": "ComfyUI Media Engine",
        "port": 8188,
        "script": "services/comfyui_service.py",
        "log": "logs/comfyui.log",
        "pid_file": "logs/pids/comfyui.pid",
        "desc": "Local AI Image & Video Diffusion Server",
    },
    "tts": {
        "name": "Kokoro Neural TTS",
        "port": 8880,
        "script": "services/tts_service.py",
        "log": "logs/tts.log",
        "pid_file": "logs/pids/tts.pid",
        "desc": "Local Neural Speech & Voice Generator",
    },
    "n8n": {
        "name": "n8n Workflow Daemon",
        "port": 5678,
        "script": "services/n8n_service.py",
        "log": "logs/n8n.log",
        "pid_file": "logs/pids/n8n.pid",
        "desc": "Local Workflow Automation Bridge",
    },
    "backend": {
        "name": "FastAPI Studio Core",
        "port": 8000,
        "script": None,
        "log": "logs/app.log",
        "pid_file": "logs/pids/backend.pid",
        "desc": "Core Pipeline & Database Orchestrator",
    },
}


def is_port_in_use(port: int) -> bool:
    if not port:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_pid_from_file(pid_path: Path) -> int:
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text(encoding="utf-8").strip())
            # Check if process is still running
            os.kill(pid, 0)
            return pid
        except Exception:
            return 0
    return 0


def get_python_exec() -> str:
    venv_py = BASE_DIR / "backend" / ".venv" / "bin" / "python3"
    if venv_py.exists():
        return str(venv_py)
    return "python3"


@router.get("/status")
async def get_all_services_status():
    result = []
    pid_dir = BASE_DIR / "logs" / "pids"
    pid_dir.mkdir(parents=True, exist_ok=True)

    for svc_key, meta in SERVICES_META.items():
        port = meta["port"]
        port_active = is_port_in_use(port)
        pid_file = BASE_DIR / meta["pid_file"]
        pid = get_pid_from_file(pid_file)

        is_running = port_active or pid > 0

        result.append(
            {
                "key": svc_key,
                "name": meta["name"],
                "port": port,
                "running": is_running,
                "pid": pid if pid > 0 else (None if not is_running else "Active"),
                "log_file": meta["log"],
                "description": meta["desc"],
                "can_toggle": svc_key != "backend",
            }
        )
    return {"services": result}


@router.post("/{service_key}/start")
async def start_service(service_key: str):
    if service_key not in SERVICES_META:
        raise HTTPException(status_code=404, detail=f"Service '{service_key}' not found.")

    meta = SERVICES_META[service_key]
    if not meta["script"]:
        return {"message": f"Service '{meta['name']}' is managed by master process.", "running": True}

    # Check if already running
    if is_port_in_use(meta["port"]):
        return {"message": f"Service '{meta['name']}' is already running on port {meta['port']}.", "running": True}

    script_path = BASE_DIR / meta["script"]
    log_path = BASE_DIR / meta["log"]
    pid_file = BASE_DIR / meta["pid_file"]
    py_bin = get_python_exec()

    if not script_path.exists():
        raise HTTPException(status_code=500, detail=f"Script {meta['script']} not found.")

    try:
        log_file = open(log_path, "a", encoding="utf-8")
        proc = subprocess.Popen(
            [py_bin, str(script_path)],
            cwd=str(BASE_DIR),
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
        )
        pid_file.write_text(str(proc.pid), encoding="utf-8")
        logger.info(f"Started service {service_key} with PID {proc.pid}")
        return {"message": f"Service '{meta['name']}' started successfully.", "running": True, "pid": proc.pid}
    except Exception as e:
        logger.error(f"Failed to start service {service_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to launch service: {e}")


@router.post("/{service_key}/stop")
async def stop_service(service_key: str):
    if service_key not in SERVICES_META:
        raise HTTPException(status_code=404, detail=f"Service '{service_key}' not found.")

    if service_key == "backend":
        raise HTTPException(status_code=400, detail="Cannot stop core Backend API from itself.")

    meta = SERVICES_META[service_key]
    pid_file = BASE_DIR / meta["pid_file"]
    pid = get_pid_from_file(pid_file)

    killed = False
    if pid > 0:
        try:
            os.kill(pid, signal.SIGTERM)
            killed = True
        except Exception:
            pass

    # Also kill by port if running
    port = meta["port"]
    if port and is_port_in_use(port):
        try:
            # kill process listening on port
            out = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).strip()
            for p in out.split():
                if int(p) != os.getpid():
                    os.kill(int(p), signal.SIGTERM)
                    killed = True
        except Exception:
            pass

    if pid_file.exists():
        try:
            pid_file.unlink()
        except Exception:
            pass

    logger.info(f"Stopped service {service_key}")
    return {"message": f"Service '{meta['name']}' stopped.", "running": False}


@router.post("/stop-unused")
async def stop_unused_services():
    """
    Stops background services not currently needed to instantly free system RAM and CPU.
    """
    stopped = []
    # If OpenRouter is enabled, Ollama can be safely stopped
    openrouter_active = os.environ.get("OPENROUTER_ENABLED", "false").lower() in ("true", "1", "yes")

    to_stop = ["comfyui", "n8n"]
    if openrouter_active:
        to_stop.append("ollama")

    for svc_key in to_stop:
        meta = SERVICES_META[svc_key]
        pid_file = BASE_DIR / meta["pid_file"]
        pid = get_pid_from_file(pid_file)
        if pid > 0 or is_port_in_use(meta["port"]):
            try:
                await stop_service(svc_key)
                stopped.append(meta["name"])
            except Exception:
                pass

    return {
        "message": f"Freed system resources. Stopped {len(stopped)} unused tools: {', '.join(stopped) if stopped else 'None were running.'}",
        "stopped_count": len(stopped),
        "stopped": stopped,
    }
