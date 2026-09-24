import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event, Engine

from app.main import app
from app.api.deps import get_db_session
from app.models.base import Base
from app.models.scene import Scene
from app.repositories.scene_repo import SceneRepository

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_session():
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


@pytest_asyncio.fixture
async def client(test_session: AsyncSession):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db_session] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_project_endpoints(client: AsyncClient):
    # 1. Create Project
    create_payload = {
        "title": "Five Little Ducks Go Swimming",
        "topic": "Five colorful ducklings explore a sunny pond",
        "language": "en",
        "duration_min": 5,
        "duration_max": 7,
        "video_type": "Nursery Rhyme",
        "visual_style": "3D Cartoon",
        "target_age": "Kids",
    }
    res = await client.post("/api/v1/projects/", json=create_payload)
    assert res.status_code == 201
    project_data = res.json()
    project_id = project_data["id"]
    assert project_data["title"] == create_payload["title"]
    assert project_data["status"] == "DRAFT"

    # 2. List Projects
    res = await client.get("/api/v1/projects/")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) == 1
    assert projects[0]["id"] == project_id

    # 3. Get Project Detail
    res = await client.get(f"/api/v1/projects/{project_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["id"] == project_id
    assert "characters" in detail
    assert "scenes" in detail
    assert "jobs" in detail
    assert len(detail["jobs"]) == 1  # auto-initialized DRAFT job

    # 4. Patch Project
    patch_payload = {"title": "Five Little Ducks Adventure", "status": "PLANNING"}
    res = await client.patch(f"/api/v1/projects/{project_id}", json=patch_payload)
    assert res.status_code == 200
    assert res.json()["title"] == "Five Little Ducks Adventure"
    assert res.json()["status"] == "PLANNING"

    # 5. Delete Project
    res = await client.delete(f"/api/v1/projects/{project_id}")
    assert res.status_code == 204

    # Verify not found after delete
    res = await client.get(f"/api/v1/projects/{project_id}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_job_endpoints(client: AsyncClient):
    # Create project first
    res = await client.post(
        "/api/v1/projects/",
        json={"title": "Job Test Project", "topic": "Testing Jobs API"},
    )
    project_id = res.json()["id"]

    # List jobs
    res = await client.get(f"/api/v1/jobs/project/{project_id}")
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) == 1
    job_id = jobs[0]["id"]

    # Update job progress
    res = await client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"status": "RENDERING", "current_step": "SCENE_002", "progress": 40},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "RENDERING"
    assert res.json()["progress"] == 40

    # Retry job
    res = await client.post(f"/api/v1/jobs/{job_id}/retry")
    assert res.status_code == 200
    assert res.json()["error"] is None


@pytest.mark.asyncio
async def test_character_endpoints(client: AsyncClient):
    res = await client.post(
        "/api/v1/projects/",
        json={"title": "Character API Test", "topic": "Testing Characters"},
    )
    project_id = res.json()["id"]

    chars_payload = [
        {
            "name": "Ducky",
            "type": "animal",
            "appearance": "Cute yellow duckling",
            "colors": ["yellow", "orange"],
            "clothing": "Blue sailor hat",
        }
    ]
    res = await client.post(
        f"/api/v1/characters/project/{project_id}",
        json=chars_payload,
    )
    assert res.status_code == 201
    assert len(res.json()) == 1
    assert res.json()[0]["name"] == "Ducky"

    # Get character bible
    res = await client.get(f"/api/v1/characters/project/{project_id}")
    assert res.status_code == 200
    assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_scene_regeneration_endpoint(client: AsyncClient, test_session: AsyncSession):
    res = await client.post(
        "/api/v1/projects/",
        json={"title": "Scene Test", "topic": "Testing Scenes"},
    )
    project_id = res.json()["id"]

    # Insert a completed scene
    scene_repo = SceneRepository(test_session)
    scene = await scene_repo.create(
        Scene(
            project_id=project_id,
            scene_number=1,
            duration=5.0,
            environment="pond",
            status="COMPLETED",
            render_path="/renders/scene_001.mp4",
        )
    )

    # Trigger individual scene regeneration
    res = await client.post(f"/api/v1/scenes/{scene.id}/regenerate")
    assert res.status_code == 200
    updated_scene = res.json()
    assert updated_scene["status"] == "PENDING"
    assert updated_scene["render_path"] is None


@pytest.mark.asyncio
async def test_asset_endpoints(client: AsyncClient):
    res = await client.post(
        "/api/v1/projects/",
        json={"title": "Asset API Test", "topic": "Testing Assets"},
    )
    project_id = res.json()["id"]

    # Create asset
    asset_payload = {
        "project_id": project_id,
        "asset_type": "music",
        "file_path": "/projects/test/music.wav",
        "status": "READY",
    }
    res = await client.post(f"/api/v1/assets/project/{project_id}", json=asset_payload)
    assert res.status_code == 201
    assert res.json()["asset_type"] == "music"

    # List assets
    res = await client.get(f"/api/v1/assets/project/{project_id}")
    assert res.status_code == 200
    assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_log_security_and_reading(client: AsyncClient):
    # 1. List logs
    res = await client.get("/api/v1/logs/")
    assert res.status_code == 200
    assert "logs" in res.json()

    # 2. Read valid log (app.log)
    res = await client.get("/api/v1/logs/app.log")
    assert res.status_code == 200
    assert res.json()["filename"] == "app.log"

    # 3. Security: Path traversal attempt must be rejected with 400 Bad Request
    res = await client.get("/api/v1/logs/../../etc/passwd")
    assert res.status_code in (400, 404)

    # 4. Security: Unauthorized file request must be rejected
    res = await client.get("/api/v1/logs/unauthorized_secrets.txt")
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_dashboard_stats(client: AsyncClient):
    # Create project
    await client.post(
        "/api/v1/projects/",
        json={"title": "Dashboard Metric Project", "topic": "Metrics"},
    )

    res = await client.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_projects" in data
    assert data["total_projects"] >= 1
    assert "active_jobs" in data
    assert "storage_used_bytes" in data
