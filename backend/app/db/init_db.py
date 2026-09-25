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

        # Migrate missing columns on scenes table if SQLite database already existed
        def migrate_sqlite_columns(sync_conn):
            try:
                res = sync_conn.exec_driver_sql("PRAGMA table_info(scenes);")
                existing_cols = {row[1] for row in res.fetchall()}
                new_columns = [
                    ("start_time", "FLOAT"),
                    ("end_time", "FLOAT"),
                    ("negative_prompt", "TEXT"),
                    ("start_frame", "VARCHAR(512)"),
                    ("end_frame", "VARCHAR(512)"),
                    ("reference_image", "VARCHAR(512)"),
                    ("previous_scene_id", "VARCHAR(64)"),
                    ("next_scene_id", "VARCHAR(64)"),
                    ("generation_status", "VARCHAR(32)"),
                    ("generation_attempt", "INTEGER DEFAULT 0"),
                    ("provider", "VARCHAR(64)"),
                    ("provider_request_id", "VARCHAR(128)"),
                    ("video_url", "VARCHAR(512)"),
                    ("local_video_path", "VARCHAR(512)"),
                    ("error_message", "TEXT"),
                ]
                for col_name, col_type in new_columns:
                    if col_name not in existing_cols:
                        sync_conn.exec_driver_sql(f"ALTER TABLE scenes ADD COLUMN {col_name} {col_type};")
            except Exception as e:
                logger.warning(f"Column migration check note: {e}")

        await conn.run_sync(migrate_sqlite_columns)
    await engine.dispose()
    logger.info("Database tables initialized successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())
