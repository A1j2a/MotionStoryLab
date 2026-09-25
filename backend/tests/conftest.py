import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import event

from app.main import app
from app.api.deps import get_db_session
from app.models.base import Base
import app.db.session as db_session_mod

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_session():
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

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

    orig_async_session_local = db_session_mod.AsyncSessionLocal
    db_session_mod.AsyncSessionLocal = async_session

    async with async_session() as session:
        yield session

    db_session_mod.AsyncSessionLocal = orig_async_session_local

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(test_session: AsyncSession):
    async def override_get_db_session():
        yield test_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


from unittest.mock import AsyncMock, patch
import app.api.v1.projects as projects_mod


@pytest.fixture(autouse=True)
def mock_pipeline():
    with patch.object(projects_mod, "run_project_pipeline", new_callable=AsyncMock) as m:
        yield m

