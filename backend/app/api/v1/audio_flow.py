import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.api.deps import get_db_session
from app.core.config import settings
from app.models.project import Project
from app.models.job import Job, JobStatus
from app.models.asset import Asset
from app.repositories.project_repo import ProjectRepository
from app.repositories.job_repo import JobRepository
from audio.providers import get_music_provider
from audio.analyzer import analyze_audio_timeline
from audio.synthesizer import generate_subtitles_srt

router = APIRouter(prefix="/projects", tags=["audio-flow"])


async def run_song_generation_task(project_id: str):
    """Background task generating song from exact approved lyrics and running audio analysis."""
    from app.db.session import AsyncSessionLocal

    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)
    audio_dir = os.path.join(project_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    master_song_path = os.path.join(audio_dir, "master_soundtrack.wav")

    async with AsyncSessionLocal() as session:
        project_repo = ProjectRepository(session)
        job_repo = JobRepository(session)

        project = await project_repo.get(project_id)
        if not project:
            return

        meta = project.metadata_json or {}
        approved_lyrics = meta.get("approved_lyrics") or project.lyrics_text or "Singing our happy preschool song!"
        music_style = meta.get("content_package", {}).get("music_style", "Preschool Upbeat 120 BPM")
        voice_style = meta.get("content_package", {}).get("voice_style", "Warm cheerful animated storyteller")
        target_dur = max(30.0, float((project.duration_min or 1) * 60.0))

        # Update job to SONG_GENERATING
        jobs = await job_repo.list_by_project(project_id)
        if jobs:
            j = jobs[0]
            j.status = JobStatus.SONG_GENERATING
            j.current_step = "GENERATING_SONG_FROM_APPROVED_LYRICS"
            j.progress = 35
            await job_repo.update(j)

        # 1. Generate Song via MusicProvider
        music_prov = get_music_provider()
        song_file = music_prov.generate_song(
            approved_lyrics=approved_lyrics,
            music_style=music_style,
            voice_style=voice_style,
            duration_sec=target_dur,
            output_path=master_song_path,
            topic=project.topic or project.title,
        )

        # 2. Automatically analyze the generated song/audio
        timeline = analyze_audio_timeline(song_file, approved_lyrics, bpm=120)

        # 3. Generate subtitles SRT from analyzed lyric timestamps
        srt_path = os.path.join(project_dir, "subtitles.srt")
        mock_scenes = []
        for ts in timeline.get("lyrics_timestamps", []):
            mock_scenes.append({"duration": ts["end"] - ts["start"], "lyrics": ts["line"]})
        generate_subtitles_srt(mock_scenes, srt_path, total_duration_sec=timeline["duration"])

        # 4. Save Assets and Metadata in DB
        meta_copy = dict(meta)
        meta_copy["audio_timeline"] = timeline
        project.metadata_json = meta_copy
        await project_repo.update(project)

        session.add(Asset(project_id=project_id, asset_type="audio", file_path=song_file))
        session.add(Asset(project_id=project_id, asset_type="subtitles", file_path=srt_path))

        # Update Job to SONG_READY / AUDIO_ANALYZING completed
        if jobs:
            j = jobs[0]
            j.status = JobStatus.SONG_READY
            j.current_step = "SONG_AND_TIMELINE_READY"
            j.progress = 45
            await job_repo.update(j)

        await session.commit()


@router.post("/{project_id}/song/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_project_song(
    project_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 6: Generates song from exact approved lyrics and runs Step 7 Audio Analysis.
    """
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    background_tasks.add_task(run_song_generation_task, project_id)
    return {
        "status": "started",
        "project_id": project_id,
        "message": "Song generation from approved lyrics initiated",
    }


@router.get("/{project_id}/audio-timeline", response_model=Dict[str, Any])
async def get_project_audio_timeline(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 7: Returns structured audio timeline (duration, BPM, sections, lyric timestamps).
    """
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    if "audio_timeline" in meta:
        return meta["audio_timeline"]

    # If timeline doesn't exist yet, construct baseline
    approved_lyrics = meta.get("approved_lyrics") or project.lyrics_text or "Singing our happy rhyme"
    master_song_path = os.path.join(str(settings.resolved_project_dir), project_id, "audio", "master_soundtrack.wav")
    timeline = analyze_audio_timeline(master_song_path, approved_lyrics, bpm=120)
    return timeline


@router.get("/{project_id}/song")
async def get_project_song_file(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Returns the playable master audio file."""
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    song_path = os.path.join(str(settings.resolved_project_dir), project_id, "audio", "master_soundtrack.wav")
    if not os.path.exists(song_path):
        song_path = os.path.join(str(settings.resolved_project_dir), project_id, "audio", "music.wav")
    if not os.path.exists(song_path):
        raise HTTPException(status_code=404, detail="Song file not yet generated")

    return FileResponse(song_path, media_type="audio/wav", filename=f"{project.title}_song.wav")
