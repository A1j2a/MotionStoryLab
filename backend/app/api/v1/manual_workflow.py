"""
Manual External Generation Workflow API
Handles: scene prompt-copy tracking, scene video upload, sequence confirmation, and final assembly.
NO AI video-generation calls — user generates videos externally (e.g. Google Flow).
"""
import os
import re
import sys
import shutil
import asyncio
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.api.deps import get_db_session
from app.core.config import settings
from app.models.scene import Scene
from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.repositories.scene_repo import SceneRepository
from ai.providers import get_ai_provider

router = APIRouter(prefix="/projects", tags=["manual-workflow"])
logger = logging.getLogger("studio.manual_workflow")


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: SEO Content Generation (Title, Description, Tags, Caption)
# ─────────────────────────────────────────────────────────────────────────────

class SEOPayload(BaseModel):
    topic: Optional[str] = None


@router.post("/{project_id}/seo/generate", response_model=Dict[str, Any])
async def generate_project_seo(
    project_id: str,
    payload: Optional[SEOPayload] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """Generate SEO package: YouTube Title, Description, Tags, Caption via AI with 1-click copy support."""
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    topic = (payload and payload.topic) or project.topic or project.title or "Nursery Rhymes"
    provider = get_ai_provider()

    prompt = f"""Generate a high-converting YouTube Kids SEO metadata package for the preschool topic: "{topic}".
Return ONLY a valid JSON object with these EXACT keys:
- "title": Catchy, high-CTR YouTube title with friendly emojis (must have million-view potential, e.g. "{topic} 🎶 Soothing 3D Nursery Rhyme")
- "description": Comprehensive, warm preschool YouTube description with overview, educational value, lyrics section placeholder, and subscribe CTA
- "tags": Comma-separated string of 15 high-intent preschool search keywords (e.g. "{topic.lower()}, kids songs, nursery rhymes, 3d animation, toddlers")
- "caption": Short, engaging social media / YouTube Shorts caption with 2-3 emojis and trending hashtags
"""
    system_prompt = "You are a world-class YouTube Kids SEO strategist. Return strictly valid JSON."

    try:
        res = await asyncio.to_thread(provider.generate_json, prompt, system_prompt, max_tokens=1200)
    except Exception as e:
        logger.warning(f"AI SEO generation failed: {e}")
        res = None

    if not res or not isinstance(res, dict) or not res.get("title"):
        clean = topic.strip().title()
        res = {
            "title": f"{clean} 🎶 Nursery Rhymes & Kids Songs | 3D Animation for Toddlers ✨",
            "description": f"Welcome to our magical world of preschool music and joyful discovery! 🌟\\n\\nSing, dance, and learn with cute 3D cartoon friends in this animated nursery rhyme about {clean}.\\n\\n🔔 Subscribe for weekly educational rhymes, phonics, and dance-along toddler cartoons!\\n\\n#nurseryrhymes #kidssongs #toddlerlearning #3danimation",
            "tags": f"{clean.lower()}, kids songs, nursery rhymes, toddler songs, preschool learning, 3d cartoon, rhymes for babies, baby learning, educational songs, sing along, cartoon for kids, bedtime lullaby, animation",
            "caption": f"Sing and dance along with {clean}! 🌟🎵 Learn, smile, and explore with our cute 3D cartoon friends! #kidssongs #nurseryrhymes #preschool #toddlerfun",
        }

    meta = project.metadata_json or {}
    meta["manual_seo"] = res
    project.metadata_json = meta
    await project_repo.update(project)
    await session.commit()
    return res


@router.get("/{project_id}/seo", response_model=Dict[str, Any])
async def get_project_seo(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve saved SEO package (Title, Description, Tags, Caption) for a project."""
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    seo = meta.get("manual_seo")
    if not seo:
        clean = (project.topic or project.title or "Nursery Rhymes").strip().title()
        seo = {
            "title": f"{clean} 🎶 Nursery Rhymes & Kids Songs | 3D Animation for Toddlers ✨",
            "description": f"Welcome to our magical world of preschool music and joyful discovery! 🌟\\n\\nSing, dance, and learn with cute 3D cartoon friends in this animated nursery rhyme about {clean}.\\n\\n🔔 Subscribe for weekly educational rhymes, phonics, and dance-along toddler cartoons!\\n\\n#nurseryrhymes #kidssongs #toddlerlearning #3danimation",
            "tags": f"{clean.lower()}, kids songs, nursery rhymes, toddler songs, preschool learning, 3d cartoon, rhymes for babies, baby learning, educational songs, sing along, cartoon for kids, bedtime lullaby, animation",
            "caption": f"Sing and dance along with {clean}! 🌟🎵 Learn, smile, and explore with our cute 3D cartoon friends! #kidssongs #nurseryrhymes #preschool #toddlerfun",
        }
    return seo



# ─────────────────────────────────────────────────────────────────────────────
# Scene Prompt Copy Tracking
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{project_id}/scenes/{scene_id}/mark-copied", response_model=Dict[str, Any])
async def mark_scene_prompt_copied(
    project_id: str,
    scene_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Mark a scene prompt as copied by the user. Persists state to DB."""
    scene_repo = SceneRepository(session)
    scene = await scene_repo.get(scene_id)
    if not scene or scene.project_id != project_id:
        raise HTTPException(status_code=404, detail="Scene not found")

    scene.prompt_status = "PROMPT_COPIED"
    scene.prompt_copied_at = datetime.now(timezone.utc).isoformat()
    await scene_repo.update(scene)
    await session.commit()
    return {
        "scene_id": scene_id,
        "scene_number": scene.scene_number,
        "prompt_status": scene.prompt_status,
        "prompt_copied_at": scene.prompt_copied_at,
    }


@router.get("/{project_id}/scenes/copy-status", response_model=Dict[str, Any])
async def get_copy_status(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Return prompt-copy counts and per-scene status for the project."""
    result = await session.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc())
    )
    scenes = result.scalars().all()
    total = len(scenes)
    copied = sum(1 for s in scenes if s.prompt_status and s.prompt_status != "NOT_COPIED")
    uploaded = sum(1 for s in scenes if s.prompt_status in ("VIDEO_UPLOADED", "ORDER_CONFIRMED"))
    return {
        "total_scenes": total,
        "copied_count": copied,
        "uploaded_count": uploaded,
        "scenes": [
            {
                "scene_id": s.id,
                "scene_number": s.scene_number,
                "prompt_status": s.prompt_status or "NOT_COPIED",
                "prompt_copied_at": s.prompt_copied_at,
                "uploaded_file": s.uploaded_file,
                "uploaded_duration": s.uploaded_duration,
                "scene_order": s.scene_order if s.scene_order is not None else s.scene_number,
                "lyrics": s.lyrics,
                "duration": s.duration,
            }
            for s in scenes
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Scene Video Upload
# ─────────────────────────────────────────────────────────────────────────────

def _extract_scene_number_from_filename(filename: str, total_scenes: int) -> Optional[int]:
    """Priority 1: try to extract scene number from filename deterministically."""
    name = os.path.splitext(filename)[0].lower()
    # Patterns: scene_01, scene-01, scene01, 01, s01
    patterns = [
        r"scene[_\-]?(\d+)",
        r"s(\d+)",
        r"(?:^|[_\-])(\d+)(?:[_\-]|$)",
        r"(\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, name)
        if m:
            n = int(m.group(1))
            if 1 <= n <= total_scenes:
                return n
    return None


def _probe_video_duration(path: str) -> Optional[float]:
    """Use ffprobe to extract video duration."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=15
        )
        return float(result.stdout.strip())
    except Exception:
        return None


@router.post("/{project_id}/scenes/{scene_id}/upload-video", response_model=Dict[str, Any])
async def upload_scene_video(
    project_id: str,
    scene_id: str,
    file: UploadFile = File(...),
    force_replace: bool = Form(False),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Upload an externally-generated scene video.
    Validates file type, saves to disk, probes duration, and updates scene record.
    """
    scene_repo = SceneRepository(session)
    scene = await scene_repo.get(scene_id)
    if not scene or scene.project_id != project_id:
        raise HTTPException(status_code=404, detail="Scene not found")

    # Validate file type
    allowed_exts = {".mp4", ".mov", ".webm"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Use MP4, MOV, or WEBM.")

    # Duplicate protection
    if scene.uploaded_file and not force_replace:
        return {
            "conflict": True,
            "scene_id": scene_id,
            "scene_number": scene.scene_number,
            "existing_file": os.path.basename(scene.uploaded_file),
            "message": f"Scene {scene.scene_number:02d} already has an uploaded video.",
        }

    # Save file
    project_dir = Path(str(settings.resolved_project_dir)) / project_id / "uploaded_scenes"
    project_dir.mkdir(parents=True, exist_ok=True)
    dest = project_dir / f"scene_{scene.scene_number:03d}{ext}"

    content = await file.read()
    dest.write_bytes(content)

    # Probe duration
    duration = await asyncio.to_thread(_probe_video_duration, str(dest))

    # Check duration warning (>20% deviation from planned duration)
    planned = scene.duration or 8.0
    duration_warning = None
    if duration and abs(duration - planned) > planned * 0.2:
        duration_warning = f"Scene {scene.scene_number:02d} expected ~{planned:.1f}s but uploaded video is {duration:.1f}s."

    # Update scene record
    scene.uploaded_file = str(dest)
    scene.uploaded_duration = duration
    scene.prompt_status = "VIDEO_UPLOADED"
    scene.scene_order = scene.scene_order if scene.scene_order is not None else scene.scene_number
    # Also store as local_video_path so existing assembly code can use it
    scene.local_video_path = str(dest)
    scene.render_path = str(dest)
    scene.status = "COMPLETED"
    scene.generation_status = "UPLOADED"
    await scene_repo.update(scene)
    await session.commit()

    return {
        "scene_id": scene_id,
        "scene_number": scene.scene_number,
        "prompt_status": scene.prompt_status,
        "uploaded_file": str(dest),
        "uploaded_filename": os.path.basename(str(dest)),
        "uploaded_duration": duration,
        "planned_duration": planned,
        "duration_warning": duration_warning,
    }


@router.post("/{project_id}/scenes/batch-upload", response_model=Dict[str, Any])
async def batch_upload_scenes(
    project_id: str,
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Batch-upload multiple scene videos at once.
    Auto-maps by filename (scene_01.mp4 → Scene 1). Returns unresolved for manual assignment.
    """
    result_list = await session.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc())
    )
    scenes = result_list.scalars().all()
    total = len(scenes)
    scenes_by_num = {s.scene_number: s for s in scenes}

    project_dir = Path(str(settings.resolved_project_dir)) / project_id / "uploaded_scenes"
    project_dir.mkdir(parents=True, exist_ok=True)

    results = []
    unresolved = []

    for file in files:
        filename = file.filename or "unknown.mp4"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in {".mp4", ".mov", ".webm"}:
            results.append({"filename": filename, "status": "REJECTED", "reason": "Unsupported file type"})
            continue

        scene_num = _extract_scene_number_from_filename(filename, total)
        content = await file.read()

        if scene_num and scene_num in scenes_by_num:
            scene = scenes_by_num[scene_num]
            dest = project_dir / f"scene_{scene_num:03d}{ext}"
            dest.write_bytes(content)
            duration = await asyncio.to_thread(_probe_video_duration, str(dest))
            scene.uploaded_file = str(dest)
            scene.uploaded_duration = duration
            scene.prompt_status = "VIDEO_UPLOADED"
            scene.local_video_path = str(dest)
            scene.render_path = str(dest)
            scene.status = "COMPLETED"
            scene.generation_status = "UPLOADED"
            await session.flush()
            results.append({
                "filename": filename,
                "status": "UPLOADED",
                "scene_number": scene_num,
                "duration": duration,
            })
        else:
            # Cannot auto-map — store temporarily for manual assignment
            tmp_path = project_dir / f"unresolved_{filename}"
            tmp_path.write_bytes(content)
            duration = await asyncio.to_thread(_probe_video_duration, str(tmp_path))
            unresolved.append({
                "filename": filename,
                "tmp_path": str(tmp_path),
                "duration": duration,
            })
            results.append({"filename": filename, "status": "NEEDS_ASSIGNMENT"})

    await session.commit()
    return {
        "results": results,
        "unresolved": unresolved,
        "total_uploaded": sum(1 for r in results if r["status"] == "UPLOADED"),
        "needs_assignment": len(unresolved),
    }


@router.post("/{project_id}/scenes/assign-video", response_model=Dict[str, Any])
async def assign_unresolved_video(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
    scene_number: int = Form(...),
    tmp_path: str = Form(...),
    force_replace: bool = Form(False),
):
    """Manually assign a previously uploaded unresolved video file to a specific scene."""
    result = await session.execute(
        select(Scene).where(Scene.project_id == project_id, Scene.scene_number == scene_number)
    )
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene {scene_number} not found")

    if scene.uploaded_file and not force_replace:
        return {"conflict": True, "scene_number": scene_number,
                "existing_file": os.path.basename(scene.uploaded_file),
                "message": f"Scene {scene_number:02d} already has an uploaded video."}

    # Move tmp file to proper scene slot
    project_dir = Path(str(settings.resolved_project_dir)) / project_id / "uploaded_scenes"
    ext = os.path.splitext(tmp_path)[1].lower()
    dest = project_dir / f"scene_{scene_number:03d}{ext}"
    if Path(tmp_path).exists():
        Path(tmp_path).rename(dest)
    elif not dest.exists():
        raise HTTPException(status_code=400, detail="Temporary file not found")

    duration = await asyncio.to_thread(_probe_video_duration, str(dest))

    scene.uploaded_file = str(dest)
    scene.uploaded_duration = duration
    scene.prompt_status = "VIDEO_UPLOADED"
    scene.local_video_path = str(dest)
    scene.render_path = str(dest)
    scene.status = "COMPLETED"
    scene.generation_status = "UPLOADED"
    scene_repo = SceneRepository(session)
    await scene_repo.update(scene)
    await session.commit()

    return {"scene_number": scene_number, "status": "ASSIGNED", "duration": duration}


# ─────────────────────────────────────────────────────────────────────────────
# Sequence Confirmation + Final Assembly
# ─────────────────────────────────────────────────────────────────────────────

class ConfirmSequencePayload(BaseModel):
    scene_order: List[int]  # List of scene_numbers in final confirmed order


@router.post("/{project_id}/scenes/confirm-sequence", response_model=Dict[str, Any])
async def confirm_scene_sequence(
    project_id: str,
    payload: ConfirmSequencePayload,
    session: AsyncSession = Depends(get_db_session),
):
    """User confirms the final scene sequence. Updates scene_order on each scene."""
    result = await session.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc())
    )
    scenes = result.scalars().all()
    scenes_by_num = {s.scene_number: s for s in scenes}

    for order_idx, scene_num in enumerate(payload.scene_order, start=1):
        scene = scenes_by_num.get(scene_num)
        if scene:
            scene.scene_order = order_idx
            if scene.prompt_status in ("VIDEO_UPLOADED", "ORDER_CONFIRMED"):
                scene.prompt_status = "ORDER_CONFIRMED"

    await session.commit()
    return {
        "confirmed": True,
        "sequence": payload.scene_order,
        "message": f"Scene sequence confirmed for {len(payload.scene_order)} scenes.",
    }


@router.get("/{project_id}/assembly/readiness", response_model=Dict[str, Any])
async def check_assembly_readiness(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Pre-flight check before final video assembly.
    Verifies: all scenes have uploaded videos, audio exists, SRT exists.
    """
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await session.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc())
    )
    scenes = result.scalars().all()

    meta = project.metadata_json or {}
    project_dir = Path(str(settings.resolved_project_dir)) / project_id

    # Check audio
    audio_path = project_dir / "audio" / "song.mp3"
    alt_audio = project_dir / "audio" / "song.wav"
    audio_ok = audio_path.exists() or alt_audio.exists()
    audio_file = str(audio_path) if audio_path.exists() else (str(alt_audio) if alt_audio.exists() else None)

    # Check SRT
    srt_path = project_dir / "subtitles.srt"
    alt_srt = project_dir / "audio" / "lyrics.srt"
    srt_ok = srt_path.exists() or alt_srt.exists()

    # Check scenes
    total = len(scenes)
    uploaded = [s for s in scenes if s.uploaded_file and Path(s.uploaded_file).exists()]
    missing = [s.scene_number for s in scenes if not (s.uploaded_file and Path(s.uploaded_file).exists())]

    # Check sequence confirmed
    confirmed_count = sum(1 for s in scenes if s.prompt_status == "ORDER_CONFIRMED")

    ready = (total > 0 and len(missing) == 0 and audio_ok)
    return {
        "ready": ready,
        "total_scenes": total,
        "uploaded_scenes": len(uploaded),
        "missing_scenes": missing,
        "audio_available": audio_ok,
        "audio_file": audio_file,
        "srt_available": srt_ok,
        "sequence_confirmed": confirmed_count == total and total > 0,
        "topic": project.topic,
        "title": project.title,
    }


@router.post("/{project_id}/assembly/generate-final-video", response_model=Dict[str, Any])
async def generate_final_video_from_uploads(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Final video assembly using uploaded scene videos + existing song audio + SRT.
    Uses existing FFmpeg compositor. No AI video generation.
    """
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await session.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(
            Scene.scene_order.asc(), Scene.scene_number.asc()
        )
    )
    scenes = result.scalars().all()

    # Validate all scene videos exist
    missing = [
        s.scene_number for s in scenes
        if not (s.uploaded_file and Path(s.uploaded_file).exists())
    ]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing scene videos for scenes: {missing}. Upload all scenes before generating final video."
        )

    project_dir = Path(str(settings.resolved_project_dir)) / project_id
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    final_video = output_dir / "final_video.mp4"

    # Find audio robustly (master_soundtrack.wav, song.mp3, etc.)
    audio_file = None
    for cand_name in ["master_soundtrack.wav", "song.mp3", "song.wav", "full_song.mp3", "full_song.wav"]:
        cand_p = project_dir / "audio" / cand_name
        if cand_p.exists():
            audio_file = str(cand_p)
            break
    if not audio_file:
        for ext in ("*.wav", "*.mp3", "*.m4a", "*.aac", "*.ogg"):
            audio_matches = list((project_dir / "audio").glob(ext)) or list(project_dir.glob(ext))
            if audio_matches:
                audio_file = str(audio_matches[0])
                break

    # Find SRT robustly
    srt_file = None
    for cand_srt in [project_dir / "subtitles.srt", project_dir / "audio" / "subtitles.srt", project_dir / "audio" / "lyrics.srt"]:
        if cand_srt.exists():
            srt_file = str(cand_srt)
            break
    if not srt_file:
        srt_matches = list(project_dir.glob("*.srt")) or list((project_dir / "audio").glob("*.srt"))
        if srt_matches:
            srt_file = str(srt_matches[0])

    # Build ordered list of uploaded scene video paths
    scene_video_paths = [Path(s.uploaded_file) for s in scenes]

    try:
        final_path = await asyncio.to_thread(
            _assemble_final_video,
            scene_video_paths=scene_video_paths,
            audio_file=audio_file,
            srt_file=srt_file,
            output_path=final_video,
        )

        # Probe final video info
        duration = _probe_video_duration(str(final_path))

        # Update project status
        meta = dict(project.metadata_json or {})
        meta["final_video_path"] = str(final_path)
        project.metadata_json = meta
        await project_repo.update(project)
        await session.commit()

        return {
            "status": "completed",
            "final_video": str(final_path),
            "duration": duration,
            "message": "Final video assembled successfully from uploaded scene videos.",
        }
    except Exception as e:
        logger.error(f"Final video assembly failed for {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Assembly failed: {str(e)}")


def _assemble_final_video(
    scene_video_paths: List[Path],
    audio_file: Optional[str],
    srt_file: Optional[str],
    output_path: Path,
) -> Path:
    """
    Concatenate scene videos, overlay audio and SRT subtitles using FFmpeg.
    Reuses the existing project's FFmpeg capabilities.
    """
    import tempfile

    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg" or "/usr/local/bin/ffmpeg" or "ffmpeg"

    # Write concat list
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in scene_video_paths:
            f.write(f"file '{str(p)}'\n")
        concat_list = f.name

    # Step 1: Concatenate all scenes (re-encode to ensure compatibility)
    concat_output = output_path.parent / "scenes_concat.mp4"
    concat_cmd = [
        ffmpeg_bin, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:v", "libx264", "-preset", "fast",
        "-crf", "20", "-pix_fmt", "yuv420p",
        "-an",  # no audio from scenes — we'll overlay song
        str(concat_output)
    ]
    subprocess.run(concat_cmd, check=True, capture_output=True, text=True, timeout=600)

    # Step 2: Overlay audio + optional SRT subtitles
    subtitles_burned = False
    if srt_file and Path(srt_file).exists():
        try:
            # Escape path properly for libavfilter
            escaped_srt = str(srt_file).replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
            sub_filter = f"subtitles='{escaped_srt}'"

            cmd = [ffmpeg_bin, "-y", "-i", str(concat_output)]
            if audio_file and Path(audio_file).exists():
                cmd += [
                    "-i", audio_file,
                    "-vf", sub_filter,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k",
                    "-shortest",
                    str(output_path),
                ]
            else:
                cmd += [
                    "-vf", sub_filter,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-an",
                    str(output_path),
                ]
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
            subtitles_burned = True
        except Exception as srt_err:
            logger.warning(f"Subtitles burning failed ({srt_err}). Falling back to clean video+audio muxing...")

    if not subtitles_burned:
        cmd = [ffmpeg_bin, "-y", "-i", str(concat_output)]
        if audio_file and Path(audio_file).exists():
            cmd += [
                "-i", audio_file,
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(output_path),
            ]
        else:
            cmd += ["-map", "0:v:0", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(output_path)]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)

    # Cleanup temp
    try:
        os.unlink(concat_list)
        if concat_output.exists():
            concat_output.unlink()
    except Exception:
        pass

    return output_path


@router.get("/{project_id}/assembly/final-video")
@router.head("/{project_id}/assembly/final-video")
async def serve_final_video(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Stream/download the assembled final video."""
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    video_path = meta.get("final_video_path")

    if not video_path or not Path(video_path).exists():
        # Try default location
        default = Path(str(settings.resolved_project_dir)) / project_id / "output" / "final_video.mp4"
        if default.exists():
            video_path = str(default)
        else:
            raise HTTPException(status_code=404, detail="Final video not yet assembled")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        content_disposition_type="inline",
        filename=f"final_video_{project_id[:8]}.mp4",
    )
