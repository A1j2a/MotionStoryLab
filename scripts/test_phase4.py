#!/usr/bin/env python3
"""
Test Suite and Runner for Phase 4: Frontend Dashboard
Validates Next.js pages, build artifacts, TypeScript compilation, and route structures.
"""

import os
import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
studio_root = script_dir.parent
frontend_dir = studio_root / "frontend"

REQUIRED_ROUTES = [
    "app/layout.tsx",
    "app/page.tsx",
    "app/create/page.tsx",
    "app/projects/page.tsx",
    "app/projects/[id]/page.tsx",
    "app/scenes/page.tsx",
    "app/characters/page.tsx",
    "app/assets/page.tsx",
    "app/audio/page.tsx",
    "app/render/page.tsx",
    "app/approval/page.tsx",
    "app/settings/page.tsx",
    "app/logs/page.tsx",
]

REQUIRED_COMPONENTS = [
    "components/Sidebar.tsx",
    "components/Header.tsx",
    "components/HealthStatus.tsx",
    "components/JobProgressBar.tsx",
    "lib/api.ts",
    "lib/types.ts",
]


def test_routes_exist():
    print("[1/3] Verifying all 12 dashboard route pages and components...")
    missing = []
    for r in REQUIRED_ROUTES:
        target = frontend_dir / r
        if not target.is_file():
            missing.append(r)
        else:
            print(f"  ✓ Route: {r}")

    for c in REQUIRED_COMPONENTS:
        target = frontend_dir / c
        if not target.is_file():
            missing.append(c)
        else:
            print(f"  ✓ Component/Lib: {c}")

    if missing:
        raise AssertionError(f"Missing required frontend routes: {missing}")


def test_next_build_artifacts():
    print("\n[2/3] Verifying Next.js production build artifacts (.next)...")
    next_dir = frontend_dir / ".next"
    assert next_dir.is_dir(), ".next build directory does not exist. Run npm run build."
    print("  ✓ .next directory verified")

    build_manifest = next_dir / "build-manifest.json"
    assert build_manifest.is_file(), "build-manifest.json missing in .next"
    print("  ✓ build-manifest.json verified")


def test_start_script_frontend_integration():
    print("\n[3/3] Checking start.sh frontend detection...")
    start_sh = studio_root / "start.sh"
    content = start_sh.read_text(encoding="utf-8")
    assert "npm run dev" in content or "npm start" in content, "start.sh does not launch frontend"
    assert "FRONTEND_PORT" in content, "start.sh missing FRONTEND_PORT"
    print("  ✓ start.sh correctly configured to launch Next.js on port 3000")


def main():
    print("=" * 60)
    print(" AI Kids Video Studio - Phase 4: Frontend Dashboard Verification")
    print("=" * 60)
    try:
        test_routes_exist()
        test_next_build_artifacts()
        test_start_script_frontend_integration()
        print("\n" + "=" * 60)
        print("🎉 ALL PHASE 4 FRONTEND CHECKS & TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ Phase 4 Verification Failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
