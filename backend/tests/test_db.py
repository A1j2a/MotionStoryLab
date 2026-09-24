import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event, Engine

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

# In-memory test database URL
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_project_crud(db_session: AsyncSession):
    repo = ProjectRepository(db_session)

    # 1. Create
    project = Project(
        title="The Little Train Finds Five Animals",
        topic="Five friendly animals board a colorful steam train in the magical forest",
        language="en",
        duration_min=5,
        duration_max=7,
        video_type="Nursery Rhyme",
        visual_style="3D Cartoon",
        target_age="Kids",
        status="DRAFT",
    )
    created = await repo.create(project)
    assert created.id is not None
    assert created.title == "The Little Train Finds Five Animals"
    assert created.status == "DRAFT"

    # 2. Get
    retrieved = await repo.get(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id

    # 3. Update status
    updated = await repo.update_status(created.id, "PLANNING")
    assert updated is not None
    assert updated.status == "PLANNING"

    # 4. List by status
    projects = await repo.list_by_status("PLANNING")
    assert len(projects) == 1
    assert projects[0].id == created.id

    # 5. Delete
    deleted = await repo.delete(created.id)
    assert deleted is True
    assert await repo.get(created.id) is None


@pytest.mark.asyncio
async def test_job_lifecycle_and_progress(db_session: AsyncSession):
    project_repo = ProjectRepository(db_session)
    job_repo = JobRepository(db_session)

    project = await project_repo.create(
        Project(
            title="Animal Train Adventure",
            topic="Animals singing along the railway",
        )
    )

    # Create Job
    job = await job_repo.create(
        Job(
            project_id=project.id,
            status=JobStatus.PLANNING,
            current_step="GENERATE_LYRICS",
            progress=10,
        )
    )
    assert job.id is not None

    # Check active job
    active = await job_repo.get_active_job_for_project(project.id)
    assert active is not None
    assert active.id == job.id

    # Update progress
    updated_job = await job_repo.update_progress(
        job.id,
        status=JobStatus.RENDERING,
        current_step="SCENE_005",
        progress=50,
    )
    assert updated_job.status == JobStatus.RENDERING
    assert updated_job.current_step == "SCENE_005"
    assert updated_job.progress == 50

    # Complete job
    completed_job = await job_repo.update_progress(
        job.id,
        status=JobStatus.COMPLETED,
        current_step="DONE",
        progress=100,
    )
    assert completed_job.status == JobStatus.COMPLETED

    # No more active jobs
    no_active = await job_repo.get_active_job_for_project(project.id)
    assert no_active is None


@pytest.mark.asyncio
async def test_character_bible_repository(db_session: AsyncSession):
    project_repo = ProjectRepository(db_session)
    char_repo = CharacterRepository(db_session)

    project = await project_repo.create(
        Project(title="Character Test", topic="Testing Character Bible")
    )

    chars = [
        Character(
            name="Toto the Train",
            type="vehicle",
            appearance="Bright blue steam engine with big friendly animated eyes",
            colors=["blue", "yellow", "red"],
            personality="Cheerful and adventurous",
            voice="friendly_tenor",
            animation_set=["drive", "bounce", "spin"],
        ),
        Character(
            name="Daisy the Cow",
            type="animal",
            appearance="Black and white spotted friendly calf wearing a red bell",
            colors=["white", "black", "red"],
            personality="Playful and musical",
            voice="sweet_alto",
            animation_set=["wave", "dance", "jump"],
        ),
    ]

    saved_chars = await char_repo.replace_characters_for_project(project.id, chars)
    assert len(saved_chars) == 2

    loaded = await char_repo.list_by_project(project.id)
    assert len(loaded) == 2
    names = {c.name for c in loaded}
    assert "Toto the Train" in names
    assert "Daisy the Cow" in names


@pytest.mark.asyncio
async def test_scene_resumability_and_regeneration(db_session: AsyncSession):
    project_repo = ProjectRepository(db_session)
    scene_repo = SceneRepository(db_session)

    project = await project_repo.create(
        Project(title="Scene Resumability Test", topic="Testing scene ordering and resume")
    )

    # Create 5 scenes
    scenes_to_create = [
        Scene(
            scene_number=i,
            duration=6.0,
            environment="sunny_meadow",
            actions=[f"action_{i}"],
            status="PENDING",
        )
        for i in range(1, 6)
    ]
    await scene_repo.replace_scenes_for_project(project.id, scenes_to_create)

    # Complete scenes 1 to 3
    scene_1 = await scene_repo.get_by_number(project.id, 1)
    await scene_repo.update_scene_render(scene_1.id, status="COMPLETED", render_path="/path/scene_001.mp4")

    scene_2 = await scene_repo.get_by_number(project.id, 2)
    await scene_repo.update_scene_render(scene_2.id, status="COMPLETED", render_path="/path/scene_002.mp4")

    scene_3 = await scene_repo.get_by_number(project.id, 3)
    await scene_repo.update_scene_render(scene_3.id, status="COMPLETED", render_path="/path/scene_003.mp4")

    # Mark scene 4 as failed
    scene_4 = await scene_repo.get_by_number(project.id, 4)
    await scene_repo.update_scene_render(scene_4.id, status="FAILED", error="Blender frame render timeout")

    # Resumable query: get pending/failed scenes
    pending = await scene_repo.get_pending_scenes(project.id)
    assert len(pending) == 2  # scene 4 (failed) and scene 5 (pending)
    assert [s.scene_number for s in pending] == [4, 5]

    # Test scene regeneration reset
    reset_scene = await scene_repo.reset_scene(scene_4.id)
    assert reset_scene.status == "PENDING"
    assert reset_scene.error is None
    assert reset_scene.render_path is None


@pytest.mark.asyncio
async def test_asset_repository(db_session: AsyncSession):
    project_repo = ProjectRepository(db_session)
    asset_repo = AssetRepository(db_session)

    project = await project_repo.create(
        Project(title="Asset Test", topic="Testing Asset Tracking")
    )

    # Record audio assets
    await asset_repo.record_asset(
        project_id=project.id,
        asset_type="music",
        file_path="/projects/test/music.wav",
        status="READY",
    )
    await asset_repo.record_asset(
        project_id=project.id,
        asset_type="vocals",
        file_path="/projects/test/vocals.wav",
        status="READY",
    )
    await asset_repo.record_asset(
        project_id=project.id,
        asset_type="thumbnail",
        file_path="/projects/test/thumbnail.jpg",
        status="READY",
    )

    all_assets = await asset_repo.list_by_project(project.id)
    assert len(all_assets) == 3

    audio_assets = await asset_repo.list_by_project(project.id, asset_type="music")
    assert len(audio_assets) == 1
    assert audio_assets[0].file_path == "/projects/test/music.wav"


@pytest.mark.asyncio
async def test_cascade_deletion(db_session: AsyncSession):
    project_repo = ProjectRepository(db_session)
    job_repo = JobRepository(db_session)
    scene_repo = SceneRepository(db_session)

    project = await project_repo.create(
        Project(title="Cascade Delete Test", topic="Testing Cascading Deletes")
    )

    job = await job_repo.create(
        Job(project_id=project.id, status=JobStatus.DRAFT)
    )
    scene = await scene_repo.create(
        Scene(project_id=project.id, scene_number=1, environment="forest")
    )

    # Delete project
    await project_repo.delete(project.id)

    # Verify job and scene are deleted automatically via CASCADE
    assert await job_repo.get(job.id) is None
    assert await scene_repo.get(scene.id) is None


@pytest.mark.asyncio
async def test_foreign_key_enforcement(db_session: AsyncSession):
    job_repo = JobRepository(db_session)
    with pytest.raises(IntegrityError):
        await job_repo.create(
            Job(project_id="non-existent-uuid", status=JobStatus.DRAFT)
        )
