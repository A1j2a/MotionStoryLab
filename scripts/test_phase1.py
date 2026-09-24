#!/usr/bin/env python3
"""
Test Suite for Phase 1: Project Scaffold Validation
Verifies project directories, essential files, shell script syntax, and configurations.
"""

import os
import subprocess
import sys
from pathlib import Path

REQUIRED_DIRS = [
    "frontend",
    "backend",
    "backend/app",
    "backend/app/api",
    "backend/app/core",
    "backend/app/db",
    "backend/app/models",
    "backend/app/repositories",
    "backend/app/schemas",
    "backend/tests",
    "ai",
    "blender",
    "comfyui",
    "comfyui/workflows",
    "audio",
    "renderer",
    "projects",
    "n8n",
    "scripts",
    "config",
    "logs",
]

REQUIRED_FILES = [
    "start.sh",
    "stop.sh",
    ".env.example",
    "README.md",
    "backend/requirements.txt",
    "backend/pyproject.toml",
]

REQUIRED_ENV_KEYS = [
    "APP_ENV",
    "BACKEND_PORT",
    "FRONTEND_PORT",
    "DATABASE_URL",
    "OMNIROUTE_URL",
    "N8N_URL",
    "COMFYUI_URL",
    "PROJECT_DIR",
    "DEFAULT_LANGUAGE",
    "DEFAULT_DURATION_MIN",
    "DEFAULT_DURATION_MAX",
]


def test_directories(base_dir: Path):
    print("Checking required directories...")
    missing = []
    for d in REQUIRED_DIRS:
        target = base_dir / d
        if not target.is_dir():
            missing.append(d)
        else:
            print(f"  ✓ {d}")
    if missing:
        raise AssertionError(f"Missing required directories: {missing}")


def test_files(base_dir: Path):
    print("\nChecking required files...")
    missing = []
    for f in REQUIRED_FILES:
        target = base_dir / f
        if not target.is_file():
            missing.append(f)
        else:
            print(f"  ✓ {f}")
    if missing:
        raise AssertionError(f"Missing required files: {missing}")


def test_script_permissions_and_syntax(base_dir: Path):
    print("\nChecking script execution permissions and syntax...")
    for script_name in ["start.sh", "stop.sh"]:
        script_path = base_dir / script_name
        assert os.access(script_path, os.X_OK), f"{script_name} is not executable"
        print(f"  ✓ {script_name} has executable bit set")

        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error in {script_name}:\n{result.stderr}"
        print(f"  ✓ {script_name} passed bash syntax check")


def test_env_example(base_dir: Path):
    print("\nValidating .env.example content...")
    env_file = base_dir / ".env.example"
    content = env_file.read_text(encoding="utf-8")
    missing = []
    for key in REQUIRED_ENV_KEYS:
        if key not in content:
            missing.append(key)
        else:
            print(f"  ✓ Found config key: {key}")
    if missing:
        raise AssertionError(f"Missing keys in .env.example: {missing}")


def main():
    base_dir = Path(__file__).resolve().parent.parent
    print(f"Starting Phase 1 Verification for: {base_dir}\n{'=' * 50}")
    try:
        test_directories(base_dir)
        test_files(base_dir)
        test_script_permissions_and_syntax(base_dir)
        test_env_example(base_dir)
        print("\n" + "=" * 50)
        print("🎉 ALL PHASE 1 SCAFFOLD TESTS PASSED SUCCESSFULLY!")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n❌ Phase 1 Validation Failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
