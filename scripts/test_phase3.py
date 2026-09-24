#!/usr/bin/env python3
"""
Test Suite and Runner for Phase 3: FastAPI Backend
Validates REST API endpoints, routing, Pydantic schemas, and security controls.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from httpx import ASGITransport, AsyncClient

# Setup sys.path for backend
script_dir = Path(__file__).resolve().parent
studio_root = script_dir.parent
backend_dir = studio_root / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.db.init_db import init_db
from app.db.session import engine


async def run_live_api_verification():
    print("\n[Step 1/2] Verifying FastAPI Application & Endpoints Live...")
    await init_db()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://127.0.0.1:8000",
    ) as client:
        # 1. Health check
        print("  1. Testing GET /health...")
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        assert data["backend"]["status"] == "connected"
        print(f"     ✓ Backend health OK (port: {data['backend']['port']})")

        # 2. Create Project
        print("  2. Testing POST /api/v1/projects/...")
        create_payload = {
            "title": "Phase 3 Live Test Nursery Rhyme",
            "topic": "Sing-along adventure on the animal carousel",
            "language": "en",
            "duration_min": 5,
            "duration_max": 7,
            "video_type": "Nursery Rhyme",
            "visual_style": "3D Cartoon",
            "target_age": "Kids",
        }
        res = await client.post("/api/v1/projects/", json=create_payload)
        assert res.status_code == 201, f"Create project failed: {res.text}"
        project = res.json()
        project_id = project["id"]
        print(f"     ✓ Project created: {project['title']} (ID: {project_id})")

        # 3. Retrieve Project Detail
        print("  3. Testing GET /api/v1/projects/{project_id} (relational)...")
        res = await client.get(f"/api/v1/projects/{project_id}")
        assert res.status_code == 200
        detail = res.json()
        assert len(detail["jobs"]) >= 1
        print(f"     ✓ Relational details returned: {len(detail['jobs'])} job(s) present")

        # 4. Job Update & Retry
        print("  4. Testing PATCH & POST /api/v1/jobs/...")
        job_id = detail["jobs"][0]["id"]
        res = await client.patch(
            f"/api/v1/jobs/{job_id}",
            json={"status": "RENDERING", "current_step": "RENDER_SCENE_001", "progress": 35},
        )
        assert res.status_code == 200
        assert res.json()["progress"] == 35
        print(f"     ✓ Job updated to RENDERING (35%)")

        # 5. Populate Character Bible
        print("  5. Testing POST /api/v1/characters/project/{project_id}...")
        char_payload = [
            {
                "name": "Carousel Horse",
                "type": "animal",
                "appearance": "White carousel pony with golden mane and saddle",
                "colors": ["white", "gold"],
                "animation_set": ["bounce", "spin"],
            }
        ]
        res = await client.post(f"/api/v1/characters/project/{project_id}", json=char_payload)
        assert res.status_code == 201
        print(f"     ✓ Character Bible entry created: {res.json()[0]['name']}")

        # 6. Record Asset
        print("  6. Testing POST & GET /api/v1/assets/project/{project_id}...")
        asset_payload = {
            "project_id": project_id,
            "asset_type": "thumbnail",
            "file_path": "/projects/test/thumbnail.png",
            "status": "READY",
        }
        res = await client.post(f"/api/v1/assets/project/{project_id}", json=asset_payload)
        assert res.status_code == 201
        print(f"     ✓ Asset registered: {res.json()['asset_type']}")

        # 7. Dashboard Stats
        print("  7. Testing GET /api/v1/dashboard/stats...")
        res = await client.get("/api/v1/dashboard/stats")
        assert res.status_code == 200
        stats = res.json()
        print(f"     ✓ Dashboard stats verified: {stats['total_projects']} total projects, {stats['active_jobs']} active jobs")

        # 8. Security Check: Path Traversal
        print("  8. Testing Security: Path Traversal rejection on logs...")
        res = await client.get("/api/v1/logs/../../etc/passwd")
        assert res.status_code in (400, 404)
        print(f"     ✓ Path traversal securely rejected (HTTP {res.status_code})")

        # 9. Clean up test project
        print("  9. Testing DELETE /api/v1/projects/{project_id}...")
        res = await client.delete(f"/api/v1/projects/{project_id}")
        assert res.status_code == 204
        print(f"     ✓ Project cleanly deleted")

    await engine.dispose()


def run_pytest_suite():
    print("\n[Step 2/2] Running Complete Pytest Suite for Backend...")
    pytest_bin = backend_dir / ".venv" / "bin" / "pytest"
    if not pytest_bin.exists():
        pytest_bin = "pytest"

    result = subprocess.run(
        [str(pytest_bin), "-v"],
        cwd=str(backend_dir),
    )
    if result.returncode != 0:
        raise RuntimeError("Pytest backend tests failed!")


def main():
    print("=" * 60)
    print(" AI Kids Video Studio - Phase 3: FastAPI Backend Verification")
    print("=" * 60)
    try:
        asyncio.run(run_live_api_verification())
        run_pytest_suite()
        print("\n" + "=" * 60)
        print("🎉 ALL PHASE 3 BACKEND CHECKS & TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ Phase 3 Verification Failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
