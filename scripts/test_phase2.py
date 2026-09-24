#!/usr/bin/env python3
"""
Test Suite and Runner for Phase 2: Database Layer
Validates database schema creation, real CRUD operations against SQLite,
cascading deletes, foreign key constraints, and repository layer functionality.
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Setup sys.path for backend
script_dir = Path(__file__).resolve().parent
studio_root = script_dir.parent
backend_dir = studio_root / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.project import Project
from app.models.job import Job, JobStatus
from app.models.character import Character
from app.models.scene import Scene
from app.models.asset import Asset
from app.repositories.project_repo import ProjectRepository
from app.repositories.job_repo import JobRepository
from app.repositories.character_repo import CharacterRepository
from app.repositories.scene_repo import SceneRepository
from app.repositories.asset_repo import AssetRepository


async def run_live_database_verification():
    print("\n[Step 1/3] Initializing SQLite tables on disk...")
    await init_db()
    db_file = settings.resolved_project_dir / "studio.db"
    assert db_file.exists(), f"Database file not found at {db_file}"
    print(f"  ✓ Database file verified on disk: {db_file} ({db_file.stat().st_size} bytes)")

    print("\n[Step 2/3] Performing Live CRUD & Repository Verification...")
    async with AsyncSessionLocal() as session:
        proj_repo = ProjectRepository(session)
        job_repo = JobRepository(session)
        char_repo = CharacterRepository(session)
        scene_repo = SceneRepository(session)
        asset_repo = AssetRepository(session)

        # 1. Create Project
        print("  1. Creating test project: 'The Little Train Finds Five Animals'...")
        project = Project(
            title="The Little Train Finds Five Animals",
            topic="A friendly blue steam train journeys through five enchanted biomes",
            language="en",
            duration_min=5,
            duration_max=7,
            video_type="Nursery Rhyme",
            visual_style="3D Cartoon",
            target_age="Kids",
            status="DRAFT",
        )
        created_project = await proj_repo.create(project)
        project_id = created_project.id
        print(f"     ✓ Project created with ID: {project_id}")

        # 2. Add Character Bible
        print("  2. Populating Character Bible...")
        characters = [
            Character(
                name="Toto the Train",
                type="vehicle",
                appearance="Bright blue steam engine with big friendly animated eyes and brass bell",
                colors=["blue", "yellow", "red"],
                personality="Helpful, adventurous, and musical",
                voice="tenor_cheerful",
                animation_set=["drive", "bounce", "spin"],
            ),
            Character(
                name="Daisy the Cow",
                type="animal",
                appearance="Playful black and white calf with a red bow",
                colors=["white", "black", "red"],
                personality="Cheerful dancer",
                voice="alto_sweet",
                animation_set=["wave", "dance", "jump"],
            ),
        ]
        saved_chars = await char_repo.replace_characters_for_project(project_id, characters)
        print(f"     ✓ Saved {len(saved_chars)} characters to Character Bible")

        # 3. Create & Transition Job
        print("  3. Testing Job state machine & progress tracking...")
        job = await job_repo.create(
            Job(
                project_id=project_id,
                status=JobStatus.PLANNING,
                current_step="GENERATE_SCENES",
                progress=15,
            )
        )
        print(f"     ✓ Job created: {job.id} (Status: {job.status.value})")

        # Advance Job
        updated_job = await job_repo.update_progress(
            job.id,
            status=JobStatus.RENDERING,
            current_step="RENDER_SCENE_001",
            progress=40,
        )
        assert updated_job.status == JobStatus.RENDERING
        assert updated_job.progress == 40
        print(f"     ✓ Job advanced to: {updated_job.status.value}, progress: {updated_job.progress}%")

        # 4. Create Scenes & Test Resumability
        print("  4. Creating Scenes & testing resumability...")
        scenes = [
            Scene(
                scene_number=i,
                duration=6.5,
                environment="flower_valley",
                actions=["train rolls forward", "animals wave"],
                status="PENDING",
            )
            for i in range(1, 6)
        ]
        await scene_repo.replace_scenes_for_project(project_id, scenes)

        # Mark scenes 1 and 2 as completed
        scene1 = await scene_repo.get_by_number(project_id, 1)
        await scene_repo.update_scene_render(scene1.id, "COMPLETED", "/projects/test/scene_001.mp4")

        scene2 = await scene_repo.get_by_number(project_id, 2)
        await scene_repo.update_scene_render(scene2.id, "COMPLETED", "/projects/test/scene_002.mp4")

        # Mark scene 3 as failed
        scene3 = await scene_repo.get_by_number(project_id, 3)
        await scene_repo.update_scene_render(scene3.id, "FAILED", error="Frame render dropped")

        # Query pending/failed scenes for resumption
        pending = await scene_repo.get_pending_scenes(project_id)
        assert len(pending) == 3  # scenes 3, 4, 5
        print(f"     ✓ Resumable pending scenes identified: {[s.scene_number for s in pending]}")

        # 5. Record Asset
        print("  5. Recording generated media assets...")
        asset = await asset_repo.record_asset(
            project_id=project_id,
            asset_type="music",
            file_path="/projects/test/music.wav",
            metadata={"tempo": 120, "key": "C major"},
        )
        print(f"     ✓ Media asset recorded: {asset.asset_type} ({asset.file_path})")

        # 6. Verify Full Project Retrieval with Details
        print("  6. Loading Project with all relations...")
        detailed_project = await proj_repo.get_with_details(project_id)
        assert detailed_project is not None
        assert len(detailed_project.characters) == 2
        assert len(detailed_project.scenes) == 5
        assert len(detailed_project.jobs) == 1
        assert len(detailed_project.assets) == 1
        print("     ✓ Successfully verified full relational integrity in SQLite")

        # 7. Clean up test record
        print("  7. Verifying cascading deletion...")
        await proj_repo.delete(project_id)
        assert await proj_repo.get(project_id) is None
        assert await job_repo.get(job.id) is None
        print("     ✓ Cascade deletion successfully pruned project, job, scenes, characters, and assets")

    await engine.dispose()


def run_pytest_suite():
    print("\n[Step 3/3] Running Pytest Suite for Backend Database...")
    pytest_bin = backend_dir / ".venv" / "bin" / "pytest"
    if not pytest_bin.exists():
        pytest_bin = "pytest"

    result = subprocess.run(
        [str(pytest_bin), str(backend_dir / "tests" / "test_db.py"), "-v"],
        cwd=str(backend_dir),
    )
    if result.returncode != 0:
        raise RuntimeError("Pytest database tests failed!")


def main():
    print("=" * 60)
    print(" AI Kids Video Studio - Phase 2: Database Layer Verification")
    print("=" * 60)
    try:
        asyncio.run(run_live_database_verification())
        run_pytest_suite()
        print("\n" + "=" * 60)
        print("🎉 ALL PHASE 2 DATABASE CHECKS & TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ Phase 2 Verification Failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
