import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path to allow running as a standalone script
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import engine
from app.models.base import Base
# Import all models so metadata knows about them
import app.models  # noqa: F401

logger = logging.getLogger(__name__)


async def init_db():
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    logger.info("Database tables initialized successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())
