import asyncio
import os
import sys
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db import session as db_session
from app.models.project import Project
from app.models.job import Job, JobStatus
from app.models.character import Character
from app.models.scene import Scene
from app.models.asset import Asset
from app.core.config import settings

# Import AI, Audio & Rendering Modules
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from ai.content_package import generate_content_package
from ai.storyboard_generator import generate_storyboard
from ai.validator import validate_storyboard_scenes
from audio.providers import get_music_provider
from audio.analyzer import analyze_audio_timeline
from audio.synthesizer import generate_subtitles_srt
from renderer.compositor import concatenate_scenes, composite_final_video, generate_thumbnail, generate_high_ctr_thumbnail
from renderer.storybook_engine import render_illustrated_scene
from services.qc_service import run_quality_control

logger = logging.getLogger("studio.pipeline")


async def run_project_pipeline(project_id: str):
    """
    Executes the complete local-first end-to-end video generation pipeline:
    1. Content Package & Character Bible Generation -> Job 20%
    2. Exact Approved Lyrics preservation -> Source of Truth
    3. Song Generation via MusicProvider -> Job 40%
    4. Audio Analysis & Timeline Extraction (Duration, BPM, Beats, Lyric Timestamps) -> Job 50%
    5. Storyboard & Strict Scene JSON Generation (5-10s scenes) -> Job 60%
    6. Individual 3D Scene Rendering -> Job 80%
    7. Multi-track Compositing & Subtitles (FFmpeg) -> Job 90%
    8. Automated Quality Control (QC) & Ready for Review -> Job 100%
    """
    logger.info(f"Starting End-to-End Kids Video Production Pipeline for Project: {project_id}")

    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)
    audio_dir = os.path.join(project_dir, "audio")
    scenes_dir = os.path.join(project_dir, "scenes")
    os.makedirs(project_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(scenes_dir, exist_ok=True)

    async with db_session.AsyncSessionLocal() as session:
        project = await session.get(Project, project_id)
        if not project:
            logger.error(f"Project {project_id} not found")
            return

        res = await session.execute(
            select(Job).where(Job.project_id == project_id).order_by(Job.created_at.desc())
        )
        job = res.scalars().first()
        if not job:
            job = Job(
                project_id=project_id,
                status=JobStatus.CONTENT_GENERATING,
                current_step="INITIALIZING_WORKFLOW",
                progress=5,
            )
            session.add(job)
        else:
            job.status = JobStatus.CONTENT_GENERATING
            job.current_step = "CONTENT_GENERATING"
            job.progress = 10
            job.error = None

        project.status = "PROCESSING"
        await session.commit()

    try:
        # ==========================================
        # STAGE 1: COMPLETE CONTENT PACKAGE & CHARACTER BIBLE
        # ==========================================
        logger.info(f"[{project_id}] Stage 1: Generating Content Package & Character Bible for '{project.topic}'")
        topic = project.topic or project.title or "Friendly Choo Choo Train"
        
        content_pkg = generate_content_package(
            topic=topic,
            video_type=project.video_type,
            target_age=project.target_age,
            duration_minutes=float(project.duration_min or 2.0),
        )

        approved_lyrics = content_pkg["lyrics_full"]

        async with db_session.AsyncSessionLocal() as session:
            db_project = await session.get(Project, project_id)
            db_project.title = content_pkg.get("title", db_project.title)
            db_project.lyrics_text = approved_lyrics

            curr_meta = dict(db_project.metadata_json or {})
            curr_meta["content_package"] = content_pkg
            curr_meta["approved_lyrics"] = approved_lyrics
            curr_meta["visual_bible"] = content_pkg.get("visual_bible", {})
            db_project.metadata_json = curr_meta

            # Save characters to Character Bible
            await session.execute(delete(Character).where(Character.project_id == project_id))
            char_list = []
            for c in content_pkg.get("characters", []):
                char_obj = Character(
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
                session.add(char_obj)
                char_list.append(c)

            db_job = await session.get(Job, job.id)
            if db_job:
                db_job.status = JobStatus.CONTENT_APPROVED
                db_job.current_step = "CONTENT_APPROVED"
                db_job.progress = 25
            await session.commit()

        # ==========================================
        # STAGE 2: SONG GENERATION (FROM EXACT APPROVED LYRICS)
        # ==========================================
        target_duration = max(30.0, float((project.duration_min or 1) * 60.0))
        logger.info(f"[{project_id}] Stage 2: Synthesizing Song from Exact Approved Lyrics ({target_duration}s)")

        async with db_session.AsyncSessionLocal() as session:
            db_job = await session.get(Job, job.id)
            if db_job:
                db_job.status = JobStatus.SONG_GENERATING
                db_job.current_step = "GENERATING_SONG_FROM_APPROVED_LYRICS"
                db_job.progress = 35
            await session.commit()

        master_audio_path = os.path.join(audio_dir, "master_soundtrack.wav")
        music_prov = get_music_provider()
        await asyncio.to_thread(
            music_prov.generate_song,
            approved_lyrics=approved_lyrics,
            music_style=content_pkg.get("music_style", "Preschool Upbeat 120 BPM"),
            voice_style=content_pkg.get("voice_style", "Warm cheerful animated storyteller"),
            duration_sec=target_duration,
            output_path=master_audio_path,
            topic=topic,
        )

        # ==========================================
        # STAGE 3: AUDIO ANALYSIS & TIMELINE EXTRACTION
        # ==========================================
        logger.info(f"[{project_id}] Stage 3: Analyzing Generated Song Timeline")
        timeline = await asyncio.to_thread(analyze_audio_timeline, master_audio_path, approved_lyrics, 120)

        srt_path = os.path.join(project_dir, "subtitles.srt")
        mock_scenes = [{"duration": ts["end"] - ts["start"], "lyrics": ts["line"]} for ts in timeline.get("lyrics_timestamps", [])]
        await asyncio.to_thread(generate_subtitles_srt, mock_scenes, srt_path, total_duration_sec=timeline["duration"])

        async with db_session.AsyncSessionLocal() as session:
            db_project = await session.get(Project, project_id)
            meta = dict(db_project.metadata_json or {})
            meta["audio_timeline"] = timeline
            db_project.metadata_json = meta

            session.add(Asset(project_id=project_id, asset_type="audio", file_path=master_audio_path))
            session.add(Asset(project_id=project_id, asset_type="subtitles", file_path=srt_path))

            db_job = await session.get(Job, job.id)
            if db_job:
                db_job.status = JobStatus.SONG_READY
                db_job.current_step = "AUDIO_TIMELINE_READY"
                db_job.progress = 50
            await session.commit()

        # ==========================================
        # STAGE 4: STORYBOARD & STRICT SCENE JSON GENERATION
        # ==========================================
        logger.info(f"[{project_id}] Stage 4: Generating Storyboard Scenes Mapped to Lyrics & Timing")
        scenes_data = generate_storyboard(
            topic=topic,
            approved_lyrics=approved_lyrics,
            audio_timeline=timeline,
            characters=char_list,
            environments=content_pkg.get("environments", []),
            visual_bible=content_pkg.get("visual_bible", {}),
        )

        async with db_session.AsyncSessionLocal() as session:
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
                    music=s.get("music", "120 BPM upbeat"),
                    sound_effects=s.get("sound_effects", []),
                    transition=s.get("transition", "cut"),
                    status="PENDING",
                )
                session.add(scene_obj)

            db_job = await session.get(Job, job.id)
            if db_job:
                db_job.status = JobStatus.STORYBOARD_READY
                db_job.current_step = f"STORYBOARD_GENERATED_{len(scenes_data)}_SCENES"
                db_job.progress = 60
            await session.commit()

        # ==========================================
        # STAGE 5: INDIVIDUAL SCENE RENDERING (WAN FLF2V / BLENDER 3D)
        # ==========================================
        logger.info(f"[{project_id}] Stage 5: Rendering {len(scenes_data)} Scenes via VideoGenerationProvider")
        async with db_session.AsyncSessionLocal() as session:
            db_job = await session.get(Job, job.id)
            if db_job:
                db_job.status = JobStatus.SCENE_RENDERING
                db_job.current_step = "RENDERING_INDIVIDUAL_SCENES"
                db_job.progress = 65
            await session.commit()

        from ai.video_provider import get_video_provider
        from renderer.compositor import extract_final_frame
        video_provider = get_video_provider()
        logger.info(f"[{project_id}] Active Video Provider: {video_provider.name}")

        scene_video_paths = []
        num_scenes = len(scenes_data)
        prev_last_frame = None

        # Check if development test mode is active (Section 17)
        is_test_mode = os.environ.get("VIDEO_GENERATION_TEST_MODE", "false").lower() in ("true", "1", "yes")
        if is_test_mode:
            logger.info(f"[{project_id}] VIDEO_GENERATION_TEST_MODE=true: Will only render Scene 1 for verification.")

        char_bible_list = content_pkg.get("characters", [])
        env_bible_list = content_pkg.get("environments", [])
        env_bible_dict = env_bible_list[0] if (env_bible_list and len(env_bible_list) > 0) else {"name": "Preschool Environment"}

        for idx, shot in enumerate(scenes_data, start=1):
            if is_test_mode and idx > 1:
                logger.info(f"[{project_id}] Test mode active: Skipping scene {idx} of {num_scenes}.")
                break

            scene_mp4 = os.path.join(scenes_dir, f"scene_{idx:03d}.mp4")
            verse_lyrics = shot.get("lyrics", "") or f"{topic} Scene {idx}"
            scene_duration = float(shot.get("duration", 8.0))

            # Execute generation via VideoGenerationProvider abstraction
            gen_result = await asyncio.to_thread(
                video_provider.generate_scene_video,
                scene_number=idx,
                topic=topic,
                lyrics=verse_lyrics,
                duration_sec=scene_duration,
                output_mp4=scene_mp4,
                project_id=project_id,
                scene_id=shot.get("scene_id", f"scene_{idx:03d}"),
                character_bible=char_bible_list,
                environment_bible=env_bible_dict,
                camera=shot.get("camera"),
                lighting=shot.get("lighting"),
                actions=shot.get("actions"),
                start_frame_path=prev_last_frame,
                previous_scene_id=f"scene_{idx-1:03d}" if idx > 1 else None,
                next_scene_id=f"scene_{idx+1:03d}" if idx < num_scenes else None,
                custom_prompt=shot.get("video_prompt"),
            )

            # Fallback to Illustrated Storybook Engine if external provider failed and video is missing
            if not gen_result.get("success") or not os.path.exists(scene_mp4) or os.path.getsize(scene_mp4) < 1000:
                logger.warning(f"Provider {video_provider.name} did not produce video for Scene {idx}. Triggering storybook fallback...")
                await asyncio.to_thread(
                    render_illustrated_scene,
                    scene_number=idx,
                    topic=topic,
                    verse_text=verse_lyrics,
                    duration_sec=scene_duration,
                    output_mp4=scene_mp4,
                    width=1280,
                    height=720,
                    fps=24,
                )

            if os.path.exists(scene_mp4) and os.path.getsize(scene_mp4) > 1000:
                scene_video_paths.append(scene_mp4)
                # Extract final frame for subsequent scene start frame (A -> B -> C -> D continuity)
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

                db_job = await session.get(Job, job.id)
                if db_job:
                    db_job.progress = 65 + int((idx / num_scenes) * 20)
                    db_job.current_step = f"RENDERED_SCENE_{idx}_OF_{num_scenes}"
                await session.commit()

        # ==========================================
        # STAGE 6: MULTI-TRACK COMPOSITING (FFmpeg)
        # ==========================================
        logger.info(f"[{project_id}] Stage 6: Compositing Final Video with Exact Song & Subtitles")
        async with db_session.AsyncSessionLocal() as session:
            db_job = await session.get(Job, job.id)
            if db_job:
                db_job.status = JobStatus.ASSEMBLING
                db_job.current_step = "FINAL_COMPOSITING"
                db_job.progress = 88
            await session.commit()

        merged_video = os.path.join(project_dir, "merged_scenes.mp4")
        await asyncio.to_thread(concatenate_scenes, scene_video_paths, merged_video, target_duration=timeline["duration"])

        final_video_path = os.path.join(project_dir, "final.mp4")
        await asyncio.to_thread(
            composite_final_video,
            merged_video,
            master_audio_path,
            final_video_path,
            subtitles_path=srt_path,
            target_duration=timeline["duration"],
        )

        thumbnail_path = os.path.join(project_dir, "thumbnail.jpg")
        await asyncio.to_thread(
            generate_high_ctr_thumbnail,
            title=project.title,
            topic=project.topic or "Kids Song",
            output_thumbnail_path=thumbnail_path,
            video_path=final_video_path,
            character_name=char_list[0].get("name", "Hero") if char_list else "Hero",
        )

        # ==========================================
        # STAGE 7: AUTOMATED QUALITY CONTROL (QC)
        # ==========================================
        logger.info(f"[{project_id}] Stage 7: Running Automated Quality Control")
        qc_result = run_quality_control(
            project_dir=project_dir,
            project_title=project.title,
            num_scenes=num_scenes,
            approved_lyrics=approved_lyrics,
            characters=char_list,
        )

        async with db_session.AsyncSessionLocal() as session:
            session.add(Asset(project_id=project_id, asset_type="final_video", file_path=final_video_path))
            session.add(Asset(project_id=project_id, asset_type="thumbnail", file_path=thumbnail_path))

            db_proj = await session.get(Project, project_id)
            if db_proj:
                db_proj.status = "READY"
                meta = dict(db_proj.metadata_json or {})
                meta["qc_result"] = qc_result
                db_proj.metadata_json = meta

            db_job = await session.get(Job, job.id)
            if db_job:
                db_job.status = JobStatus.COMPLETED
                db_job.current_step = "READY_FOR_APPROVAL"
                db_job.progress = 100
                db_job.error = None
            await session.commit()

        logger.info(f"[{project_id}] PIPELINE COMPLETED SUCCESSFULLY! Final video: {final_video_path}")

    except Exception as e:
        logger.exception(f"[{project_id}] Pipeline execution failed: {e}")
        async with db_session.AsyncSessionLocal() as session:
            db_job = await session.get(Job, job.id)
            if db_job:
                db_job.status = JobStatus.FAILED
                db_job.current_step = "FAILED"
                db_job.error = str(e)

            db_proj = await session.get(Project, project_id)
            if db_proj:
                db_proj.status = "DRAFT"
            await session.commit()
