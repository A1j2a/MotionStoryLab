import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.api.deps import get_db_session
from app.core.config import settings
from app.models.project import Project
from app.models.scene import Scene
from app.models.character import Character
from app.models.job import Job, JobStatus
from app.models.asset import Asset
from app.repositories.project_repo import ProjectRepository
from app.repositories.scene_repo import SceneRepository
from app.repositories.job_repo import JobRepository
from ai.storyboard_generator import generate_storyboard
from ai.validator import validate_storyboard_scenes
from renderer.storybook_engine import render_illustrated_scene
from renderer.compositor import concatenate_scenes, composite_final_video, generate_thumbnail, generate_high_ctr_thumbnail

router = APIRouter(prefix="/projects", tags=["storyboard"])


@router.post("/{project_id}/storyboard/generate", response_model=List[Dict[str, Any]])
async def generate_project_storyboard(
    project_id: str,
    target_scene_duration: Optional[float] = 8.0,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 8 & 9: Generates structured Storyboard & Scene JSON from approved lyrics + audio timeline + Character Bible.
    Supports user-specified target_scene_duration (e.g. 8s, 9s, 10s).
    """
    project_repo = ProjectRepository(session)
    job_repo = JobRepository(session)

    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    approved_lyrics = meta.get("approved_lyrics") or project.lyrics_text or ""
    audio_timeline = meta.get("audio_timeline") or {
        "duration": max(30.0, float((project.duration_min or 1) * 60.0)),
        "lyrics_timestamps": [],
    }

    # Load characters
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

    target_dur = float(target_scene_duration or 8.0)

    scenes_data = generate_storyboard(
        topic=project.topic or project.title,
        approved_lyrics=approved_lyrics,
        audio_timeline=audio_timeline,
        characters=char_list,
        environments=env_list,
        visual_bible=visual_bible,
        target_scene_duration=target_dur,
    )

    # Save scenes in DB
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

    # Update Job to STORYBOARD_READY
    jobs = await job_repo.list_by_project(project_id)
    if jobs:
        j = jobs[0]
        j.status = JobStatus.STORYBOARD_READY
        j.current_step = f"STORYBOARD_GENERATED_{len(scenes_data)}_SCENES"
        j.progress = 55
        await job_repo.update(j)

    await session.commit()
    for s in scenes_data:
        if isinstance(s.get("environment"), dict):
            s["environment"] = s["environment"].get("name") or s["environment"].get("id") or "Preschool Meadow"
    return scenes_data


@router.get("/{project_id}/storyboard/validate", response_model=Dict[str, Any])
async def validate_project_storyboard(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 10: Validates storyboard against audio timeline and Character Bible before rendering.
    """
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sc_res = await session.execute(select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc()))
    db_scenes = sc_res.scalars().all()

    ch_res = await session.execute(select(Character).where(Character.project_id == project_id))
    db_chars = ch_res.scalars().all()

    meta = project.metadata_json or {}
    timeline = meta.get("audio_timeline") or {}
    total_dur = float(timeline.get("duration", 60.0))
    approved_lyrics = meta.get("approved_lyrics", "")

    scenes_list = [
        {
            "scene_number": s.scene_number,
            "duration": s.duration,
            "start_time": (s.scene_number - 1) * s.duration,
            "end_time": s.scene_number * s.duration,
            "characters": s.characters,
            "lyrics": s.lyrics,
        }
        for s in db_scenes
    ]
    chars_list = [{"name": c.name, "character_id": c.name.lower().replace(" ", "_")} for c in db_chars]

    is_valid, errors = validate_storyboard_scenes(scenes_list, chars_list, total_dur, approved_lyrics)
    return {
        "is_valid": is_valid,
        "errors": errors,
        "total_scenes": len(db_scenes),
        "total_duration": total_dur,
    }


async def render_all_scenes_task(project_id: str):
    """Renders 3D scenes individually and merges into final MP4."""
    from app.db import session as db_session

    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)
    scenes_dir = os.path.join(project_dir, "scenes")
    os.makedirs(scenes_dir, exist_ok=True)

    async with db_session.AsyncSessionLocal() as session:
        project_repo = ProjectRepository(session)
        job_repo = JobRepository(session)

        project = await project_repo.get(project_id)
        if not project:
            return

        sc_res = await session.execute(select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc()))
        scenes = sc_res.scalars().all()
        num_scenes = len(scenes)

        jobs = await job_repo.list_by_project(project_id)
        if jobs:
            j = jobs[0]
            j.status = JobStatus.SCENE_RENDERING
            j.current_step = "RENDERING_3D_SCENES"
            j.progress = 60
            await job_repo.update(j)
        await session.commit()

    from ai.video_provider import get_video_provider
    from renderer.compositor import extract_final_frame
    video_provider = get_video_provider()
    logger.info(f"[{project_id}] render_all_scenes_task using active Video Provider: {video_provider.name}")

    char_objs = await character_repo.get_by_project(project_id)
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
        }
        for c in char_objs
    ]
    meta = project.metadata_json or {}
    env_list = meta.get("content_package", {}).get("environments", [])
    env_dict = env_list[0] if (env_list and len(env_list) > 0) else {"name": "Preschool Environment"}

    scene_video_paths = []
    prev_last_frame = None

    # Check development test mode (Section 17)
    is_test_mode = os.environ.get("VIDEO_GENERATION_TEST_MODE", "false").lower() in ("true", "1", "yes")

    for idx, sc in enumerate(scenes, start=1):
        if is_test_mode and idx > 1:
            logger.info(f"[{project_id}] Test mode active: Skipping scene {idx} of {num_scenes}.")
            break

        scene_mp4 = os.path.join(scenes_dir, f"scene_{idx:03d}.mp4")
        verse_lyrics = sc.lyrics or f"{project.topic} Fun Scene {idx}"
        scene_duration = sc.duration or 8.0

        gen_result = await asyncio.to_thread(
            video_provider.generate_scene_video,
            scene_number=idx,
            topic=project.topic or project.title,
            lyrics=verse_lyrics,
            duration_sec=scene_duration,
            output_mp4=scene_mp4,
            project_id=project_id,
            scene_id=sc.id,
            character_bible=char_list,
            environment_bible=env_dict,
            camera=sc.camera,
            lighting=sc.lighting,
            actions=sc.actions,
            start_frame_path=prev_last_frame,
            previous_scene_id=f"scene_{idx-1:03d}" if idx > 1 else None,
            next_scene_id=f"scene_{idx+1:03d}" if idx < num_scenes else None,
            custom_prompt=sc.video_prompt,
        )

        # Fallback to Illustrated Storybook Engine if external provider was unconfigured or failed
        if not gen_result.get("success") or not os.path.exists(scene_mp4) or os.path.getsize(scene_mp4) < 1000:
            logger.warning(f"Provider {video_provider.name} did not produce video for Scene {idx}. Triggering storybook fallback...")
            await asyncio.to_thread(
                render_illustrated_scene,
                scene_number=idx,
                topic=project.topic or project.title,
                verse_text=verse_lyrics,
                duration_sec=scene_duration,
                output_mp4=scene_mp4,
                width=1280,
                height=720,
                fps=24,
            )

        if os.path.exists(scene_mp4) and os.path.getsize(scene_mp4) > 1000:
            scene_video_paths.append(scene_mp4)
            # Extract final frame for seamless next scene start (FLF2V)
            next_start_frame = os.path.join(scenes_dir, f"scene_{idx:03d}_last_frame.jpg")
            try:
                extract_final_frame(scene_mp4, next_start_frame)
                prev_last_frame = next_start_frame
            except Exception as fe:
                logger.debug(f"Could not extract next start frame: {fe}")

        async with db_session.AsyncSessionLocal() as session:
            stmt = select(Scene).where(Scene.project_id == project_id, Scene.scene_number == idx)
            res = await session.execute(stmt)
            db_sc = res.scalars().first()
            if db_sc:
                db_sc.status = "COMPLETED" if (os.path.exists(scene_mp4) and os.path.getsize(scene_mp4) > 1000) else "FAILED"
                db_sc.render_path = scene_mp4
                db_sc.local_video_path = scene_mp4
                db_sc.generation_status = db_sc.status
                db_sc.provider = gen_result.get("provider", video_provider.name)
                db_sc.provider_request_id = gen_result.get("request_id")
                db_sc.video_url = gen_result.get("video_url")
                db_sc.start_frame = gen_result.get("start_frame")
                db_sc.end_frame = gen_result.get("end_frame")
                db_sc.negative_prompt = gen_result.get("negative_prompt")
                db_sc.generation_attempt = gen_result.get("attempts", 1)
                db_sc.previous_scene_id = f"scene_{idx-1:03d}" if idx > 1 else None
                db_sc.next_scene_id = f"scene_{idx+1:03d}" if idx < num_scenes else None
                if not gen_result.get("success"):
                    db_sc.error = gen_result.get("error")

            j_res = await session.execute(select(Job).where(Job.project_id == project_id).order_by(Job.created_at.desc()))
            db_j = j_res.scalars().first()
            if db_j:
                db_j.progress = 60 + int((idx / num_scenes) * 20)
                db_j.current_step = f"RENDERED_SCENE_{idx}_OF_{num_scenes}"
            await session.commit()

    # Trigger assembly
    await assemble_final_video_task(project_id)


async def assemble_final_video_task(project_id: str):
    """Step 16: Multi-track FFmpeg assembly of scenes + exact song + subtitles."""
    from app.db import session as db_session

    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)
    scenes_dir = os.path.join(project_dir, "scenes")

    scene_files = sorted([
        os.path.join(scenes_dir, f)
        for f in os.listdir(scenes_dir)
        if f.endswith(".mp4") and os.path.getsize(os.path.join(scenes_dir, f)) > 1000
    ])

    audio_path = os.path.join(project_dir, "audio", "master_soundtrack.wav")
    if not os.path.exists(audio_path):
        audio_path = os.path.join(project_dir, "audio", "music.wav")
    srt_path = os.path.join(project_dir, "subtitles.srt")

    merged_video = os.path.join(project_dir, "merged_scenes.mp4")
    final_video = os.path.join(project_dir, "final.mp4")
    thumbnail_path = os.path.join(project_dir, "thumbnail.jpg")

    async with db_session.AsyncSessionLocal() as session:
        j_res = await session.execute(select(Job).where(Job.project_id == project_id).order_by(Job.created_at.desc()))
        db_j = j_res.scalars().first()
        if db_j:
            db_j.status = JobStatus.ASSEMBLING
            db_j.current_step = "FINAL_ASSEMBLY"
            db_j.progress = 85
        await session.commit()

    proj_title = "Preschool Fun"
    proj_topic = "Kids Song"
    async with db_session.AsyncSessionLocal() as session:
        p_fetch = await session.execute(select(Project).where(Project.id == project_id))
        p_found = p_fetch.scalars().first()
        if p_found:
            proj_title = p_found.title
            proj_topic = p_found.topic

    await asyncio.to_thread(concatenate_scenes, scene_files, merged_video, target_duration=60.0)
    await asyncio.to_thread(composite_final_video, merged_video, audio_path, final_video, subtitles_path=srt_path, target_duration=60.0)
    await asyncio.to_thread(
        generate_high_ctr_thumbnail,
        title=proj_title,
        topic=proj_topic,
        output_thumbnail_path=thumbnail_path,
        video_path=final_video,
    )

    async with db_session.AsyncSessionLocal() as session:
        session.add(Asset(project_id=project_id, asset_type="final_video", file_path=final_video))
        session.add(Asset(project_id=project_id, asset_type="thumbnail", file_path=thumbnail_path))

        p_res = await session.execute(select(Project).where(Project.id == project_id))
        proj = p_res.scalars().first()
        if proj:
            proj.status = "READY"

        j_res = await session.execute(select(Job).where(Job.project_id == project_id).order_by(Job.created_at.desc()))
        db_j = j_res.scalars().first()
        if db_j:
            db_j.status = JobStatus.READY_FOR_REVIEW
            db_j.current_step = "READY_FOR_PREVIEW_AND_QC"
            db_j.progress = 100
        await session.commit()


@router.post("/{project_id}/render/scenes", status_code=status.HTTP_202_ACCEPTED)
@router.post("/{project_id}/render-scenes", status_code=status.HTTP_202_ACCEPTED)
async def trigger_scene_rendering(
    project_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 13: Renders individual 3D scenes.
    """
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    background_tasks.add_task(render_all_scenes_task, project_id)
    return {
        "status": "started",
        "project_id": project_id,
        "message": "Individual 3D scene rendering started",
    }


@router.post("/{project_id}/scenes/{scene_id}/rerender", status_code=status.HTTP_200_OK)
async def rerender_single_scene(
    project_id: str,
    scene_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 23 (Regeneration System): Re-renders a single individual scene without regenerating lyrics/song/other scenes,
    then automatically rebuilds final video.
    """
    scene_repo = SceneRepository(session)
    scene = await scene_repo.get(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)

    # Reset scene
    scene.status = "PENDING"
    await scene_repo.update(scene)
    await session.commit()

    # Re-render single scene file
    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)
    scene_mp4 = os.path.join(project_dir, "scenes", f"scene_{scene.scene_number:03d}.mp4")

    from ai.video_provider import get_video_provider
    from renderer.compositor import extract_final_frame
    video_provider = get_video_provider()

    # Determine start frame from previous scene if available
    start_frame = None
    if scene.scene_number > 1:
        prev_scene_mp4 = os.path.join(project_dir, "scenes", f"scene_{scene.scene_number - 1:03d}.mp4")
        if os.path.exists(prev_scene_mp4):
            prev_last_frame = os.path.join(project_dir, "scenes", f"scene_{scene.scene_number - 1:03d}_last_frame.jpg")
            try:
                extract_final_frame(prev_scene_mp4, prev_last_frame)
                start_frame = prev_last_frame
            except Exception:
                pass

    char_objs = await CharacterRepository(session).get_by_project(project_id)
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
        }
        for c in char_objs
    ]
    meta = project.metadata_json or {} if project else {}
    env_list = meta.get("content_package", {}).get("environments", [])
    env_dict = env_list[0] if (env_list and len(env_list) > 0) else {"name": "Preschool Environment"}
    scene_dur = scene.duration or 8.0

    gen_result = await asyncio.to_thread(
        video_provider.generate_scene_video,
        scene_number=scene.scene_number,
        topic=project.topic if project else "Preschool",
        lyrics=scene.lyrics or f"Scene {scene.scene_number}",
        duration_sec=scene_dur,
        output_mp4=scene_mp4,
        project_id=project_id,
        scene_id=scene.id,
        character_bible=char_list,
        environment_bible=env_dict,
        camera=scene.camera,
        lighting=scene.lighting,
        actions=scene.actions,
        start_frame_path=start_frame,
        custom_prompt=scene.video_prompt,
    )

    # Fallback to Illustrated Storybook Engine if external provider failed and video is missing
    if not gen_result.get("success") or not os.path.exists(scene_mp4) or os.path.getsize(scene_mp4) < 1000:
        await asyncio.to_thread(
            render_illustrated_scene,
            scene_number=scene.scene_number,
            topic=project.topic if project else "Preschool",
            verse_text=scene.lyrics or f"Scene {scene.scene_number}",
            duration_sec=scene_dur,
            output_mp4=scene_mp4,
            width=1280,
            height=720,
            fps=24,
        )

    scene.status = "COMPLETED" if (os.path.exists(scene_mp4) and os.path.getsize(scene_mp4) > 1000) else "FAILED"
    scene.render_path = scene_mp4
    scene.local_video_path = scene_mp4
    scene.generation_status = scene.status
    scene.provider = gen_result.get("provider", video_provider.name)
    scene.provider_request_id = gen_result.get("request_id")
    scene.video_url = gen_result.get("video_url")
    scene.start_frame = gen_result.get("start_frame")
    scene.end_frame = gen_result.get("end_frame")
    scene.negative_prompt = gen_result.get("negative_prompt")
    scene.generation_attempt = (scene.generation_attempt or 0) + 1
    if not gen_result.get("success"):
        scene.error = gen_result.get("error")
    await scene_repo.update(scene)
    await session.commit()

    # Rebuild final assembly in background
    background_tasks.add_task(assemble_final_video_task, project_id)

    return {
        "status": "success",
        "scene_id": scene_id,
        "scene_number": scene.scene_number,
        "message": "Scene re-rendered and final video assembly initiated",
    }
