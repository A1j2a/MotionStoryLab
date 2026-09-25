from fastapi import APIRouter
from app.api.v1.projects import router as projects_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.scenes import router as scenes_router
from app.api.v1.characters import router as characters_router
from app.api.v1.assets import router as assets_router
from app.api.v1.logs import router as logs_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.storage import router as storage_router
from app.api.v1.settings_api import router as settings_router
from app.api.v1.services_api import router as services_router

# New workflow routers
from app.api.v1.topics import router as topics_router
from app.api.v1.content import router as content_router
from app.api.v1.audio_flow import router as audio_flow_router
from app.api.v1.storyboard import router as storyboard_router
from app.api.v1.qc import router as qc_router
from app.api.v1.youtube import router as youtube_router
from app.api.v1.manual_workflow import router as manual_workflow_router

api_router = APIRouter()

api_router.include_router(topics_router)
api_router.include_router(content_router)
api_router.include_router(audio_flow_router)
api_router.include_router(storyboard_router)
api_router.include_router(qc_router)
api_router.include_router(youtube_router)
api_router.include_router(manual_workflow_router)

api_router.include_router(settings_router)
api_router.include_router(services_router)
api_router.include_router(projects_router)
api_router.include_router(jobs_router)
api_router.include_router(scenes_router)
api_router.include_router(characters_router)
api_router.include_router(assets_router)
api_router.include_router(logs_router)
api_router.include_router(dashboard_router)
api_router.include_router(storage_router)
