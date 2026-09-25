import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Form
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
    from app.db import session as db_session

    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)
    audio_dir = os.path.join(project_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    master_song_path = os.path.join(audio_dir, "master_soundtrack.wav")

    async with db_session.AsyncSessionLocal() as session:
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
@router.head("/{project_id}/song")
@router.get("/{project_id}/audio-flow/stream")
@router.head("/{project_id}/audio-flow/stream")
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

    return FileResponse(song_path, media_type="audio/wav", content_disposition_type="inline", filename=f"{project.title}_song.wav")

from fastapi import UploadFile, File
import shutil
import subprocess
from app.models.scene import Scene
from app.models.character import Character
from ai.storyboard_generator import generate_storyboard
from sqlalchemy import select, delete


@router.get("/{project_id}/suno-prompt")
async def get_project_suno_prompt(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Returns high-engagement Suno AI v3.5/v4 prompt package:
    - style_prompt: Musical genre, instruments, vocal timbre & BPM tags
    - suno_title: High-CTR catchy song title
    - suno_lyrics: Full lyrics formatted with Suno structural markers ([Verse], [Chorus], [Outro])
    - suno_url: https://suno.com/create
    """
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    content_pkg = meta.get("content_package") or {}
    approved_lyrics = meta.get("approved_lyrics") or project.lyrics_text or ""

    topic = project.topic or project.title or "Happy Preschool Day"
    music_style = content_pkg.get("music_style") or project.music_style or "120 BPM upbeat preschool pop, energetic marimba, joyful acoustic guitar, handclaps"
    voice_style = content_pkg.get("voice_style") or project.voice_style or "Warm cheerful preschool female singer, clear catchy preschool melody"

    suno_style = f"Preschool Kids Anthem, {music_style}, {voice_style}, cheerful children choir background, highly catchy melody, modern upbeat preschool pop, crystal clear vocals"
    
    # Format lyrics for Suno AI tags
    suno_lyrics = approved_lyrics
    if "[Verse 1]" not in suno_lyrics and "[Chorus]" not in suno_lyrics:
        # Wrap raw text into standard Suno sections
        lines = [l.strip() for l in approved_lyrics.splitlines() if l.strip()]
        if len(lines) >= 8:
            v1 = "\n".join(lines[:4])
            ch = "\n".join(lines[4:8])
            v2 = "\n".join(lines[8:]) if len(lines) > 8 else v1
            suno_lyrics = f"[Verse 1]\n{v1}\n\n[Chorus]\n{ch}\n\n[Verse 2]\n{v2}\n\n[Chorus]\n{ch}\n\n[Outro]\nSing and play every single day!\n[End]"

    return {
        "project_id": project_id,
        "title": project.title,
        "topic": topic,
        "style_prompt": suno_style,
        "suno_title": f"{project.title} - Fun Kids Song",
        "suno_lyrics": suno_lyrics,
        "suno_url": "https://suno.com/create",
        "instructions": "1. Copy the Suno Style Prompt and Lyrics.\n2. Open suno.com/create, paste into Custom Mode, and create your song.\n3. Download the MP3/WAV and upload it below to automatically generate scene storyboards & subtitles!",
    }


@router.post("/{project_id}/audio/upload")
async def upload_project_song(
    project_id: str,
    file: UploadFile = File(...),
    lyrics: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Receives user's downloaded Suno AI song (MP3/WAV/M4A),
    converts to master_soundtrack.wav, analyzes timeline, generates synchronized subtitles (.srt),
    and automatically creates synchronized storyboard scenes!
    """
    project_repo = ProjectRepository(session)
    job_repo = JobRepository(session)

    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)
    audio_dir = os.path.join(project_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    temp_raw_path = os.path.join(audio_dir, f"upload_raw_{file.filename}")
    master_song_path = os.path.join(audio_dir, "master_soundtrack.wav")

    # 1. Save uploaded raw audio file
    with open(temp_raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Normalize / Convert to master_soundtrack.wav (44.1kHz, stereo 16-bit PCM) via FFmpeg
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg" or "ffmpeg"
    ffmpeg_cmd = [
        ffmpeg_bin, "-y",
        "-i", temp_raw_path,
        "-ar", "44100",
        "-ac", "2",
        "-c:a", "pcm_s16le",
        master_song_path
    ]
    res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if not os.path.exists(master_song_path) or os.path.getsize(master_song_path) < 1000:
        # Fallback copy if ffmpeg transcode failed
        shutil.copy(temp_raw_path, master_song_path)

    if os.path.exists(temp_raw_path) and temp_raw_path != master_song_path:
        try:
            os.remove(temp_raw_path)
        except Exception:
            pass

    meta = dict(project.metadata_json or {})
    if lyrics and lyrics.strip():
        approved_lyrics = lyrics.strip()
        project.lyrics_text = approved_lyrics
        meta["approved_lyrics"] = approved_lyrics
    else:
        approved_lyrics = meta.get("approved_lyrics") or project.lyrics_text or "Happy preschool song"

    # Mismatch Guard: If project has stale train lyrics but project topic is NOT train, auto-heal to topic package
    topic_str = (project.topic or project.title or "").lower()
    lyrics_lower = approved_lyrics.lower()
    is_mismatched = ("train" in lyrics_lower or "choo choo" in lyrics_lower or "chugga" in lyrics_lower) and ("train" not in topic_str and "rail" not in topic_str)

    if is_mismatched:
        from ai.content_package import generate_content_package
        fresh_pkg = generate_content_package(topic=project.topic or project.title, target_age=project.target_age or "1–4 Years", duration_minutes=float(project.duration_min or 2.0))
        approved_lyrics = fresh_pkg.get("lyrics_full") or fresh_pkg.get("approved_lyrics")
        project.title = fresh_pkg.get("title", project.title)
        project.lyrics_text = approved_lyrics
        meta["content_package"] = fresh_pkg
        meta["approved_lyrics"] = approved_lyrics
        meta["visual_bible"] = fresh_pkg.get("visual_bible", {})

        # Replace Character Bible
        await session.execute(delete(Character).where(Character.project_id == project_id))
        for c in fresh_pkg.get("characters", []):
            session.add(
                Character(
                    project_id=project_id,
                    name=c.get("name", "Hero"),
                    type=c.get("species", c.get("type", "character")),
                    appearance=c.get("appearance", "Cute 3D character"),
                    colors=c.get("colors", ["#facc15", "#2563eb"]),
                    clothing=c.get("clothing", ""),
                    personality=c.get("personality", "Cheerful"),
                    age=c.get("age", "Kid"),
                    voice=c.get("voice", "tenor_cheerful"),
                    animation_set=c.get("animation_set", ["walk", "wave", "dance"]),
                )
            )
        await session.flush()

    # 3. Analyze timeline (Duration, BPM, Beats, Lyric Timestamps)
    timeline = analyze_audio_timeline(master_song_path, approved_lyrics, bpm=120)

    # 4. Load characters and generate Storyboard Scenes synchronized to Audio
    char_res = await session.execute(select(Character).where(Character.project_id == project_id))
    char_objs = char_res.scalars().all()
    char_list = [
        {
            "character_id": c.name.lower().replace(" ", "_"),
            "name": c.name,
            "species": c.type,
            "appearance": c.appearance,
            "colors": c.colors,
            "clothing": c.clothing,
            "personality": c.personality,
            "voice": c.voice,
            "animation_set": c.animation_set,
        }
        for c in char_objs
    ] or meta.get("content_package", {}).get("characters", [])

    env_list = meta.get("content_package", {}).get("environments", [{"id": "env_01", "name": "Preschool World"}])
    visual_bible = meta.get("visual_bible", {})

    scenes_data = generate_storyboard(
        topic=project.topic or project.title,
        approved_lyrics=approved_lyrics,
        audio_timeline=timeline,
        characters=char_list,
        environments=env_list,
        visual_bible=visual_bible,
    )

    # 5. Generate synchronized subtitles SRT matching exact audio timeline & scenes
    srt_path = os.path.join(project_dir, "subtitles.srt")
    lyric_ts = timeline.get("lyrics_timestamps", [])
    generate_subtitles_srt(lyric_ts or scenes_data, srt_path, total_duration_sec=timeline["duration"])

    # Save scenes to DB
    await session.execute(delete(Scene).where(Scene.project_id == project_id))
    for s in scenes_data:
        scene_obj = Scene(
            project_id=project_id,
            scene_number=s.get("scene_number", 1),
            duration=float(s.get("duration", 6.0)),
            environment=s.get("environment", {}).get("name", "Preschool Environment") if isinstance(s.get("environment"), dict) else str(s.get("environment")),
            characters=[c.get("character_id", c.get("name", "hero")) if isinstance(c, dict) else str(c) for c in s.get("characters", [])],
            actions=s.get("actions", []),
            camera=s.get("camera", {}),
            lighting=s.get("lighting", {}) if isinstance(s.get("lighting"), dict) else {"type": str(s.get("lighting"))},
            dialogue=s.get("lyrics", ""),
            lyrics=s.get("lyrics", ""),
            video_prompt=s.get("video_prompt") or s.get("prompt") or s.get("visual_prompt"),
            music=s.get("music", "120 BPM upbeat"),
            sound_effects=s.get("sound_effects", []),
            transition=s.get("transition", "cut"),
            status="PENDING",
        )
        session.add(scene_obj)

    # 6. Save Assets & Metadata
    meta_copy = dict(meta)
    meta_copy["audio_timeline"] = timeline
    meta_copy["suno_audio_uploaded"] = True
    project.metadata_json = meta_copy
    await project_repo.update(project)

    session.add(Asset(project_id=project_id, asset_type="audio", file_path=master_song_path))
    session.add(Asset(project_id=project_id, asset_type="subtitles", file_path=srt_path))

    # Update Job to STORYBOARD_READY
    jobs = await job_repo.list_by_project(project_id)
    if jobs:
        j = jobs[0]
        j.status = JobStatus.STORYBOARD_READY
        j.current_step = f"SONG_UPLOADED_AND_STORYBOARD_GENERATED_{len(scenes_data)}_SCENES"
        j.progress = 60
        await job_repo.update(j)

    await session.commit()

    return {
        "status": "success",
        "message": "Suno AI Song uploaded and synchronized with storyboard & subtitles successfully!",
        "duration": timeline["duration"],
        "bpm": timeline["bpm"],
        "scenes_count": len(scenes_data),
        "timeline": timeline,
        "subtitles_url": f"/api/v1/projects/{project_id}/subtitles",
    }


@router.get("/{project_id}/subtitles")
async def download_project_subtitles(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Returns the synchronized .srt subtitle file for preview or download."""
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    srt_path = os.path.join(str(settings.resolved_project_dir), project_id, "subtitles.srt")
    if not os.path.exists(srt_path):
        raise HTTPException(status_code=404, detail="Subtitles file not yet generated")

    return FileResponse(srt_path, media_type="text/plain", filename=f"{project.title}.srt")
