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
from typing import Dict, Any, List, Optional, Tuple

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
from app.models.asset import Asset
from app.models.character import Character
from app.repositories.project_repo import ProjectRepository
from app.repositories.scene_repo import SceneRepository
from ai.providers import get_ai_provider
from renderer.compositor import generate_high_ctr_thumbnail, build_high_ctr_thumbnail_prompt, extract_short_thumbnail_title

router = APIRouter(prefix="/projects", tags=["manual-workflow"])
logger = logging.getLogger("studio.manual_workflow")


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: SEO Content Generation (Title, Description, Tags, Caption, Thumbnail)
# ─────────────────────────────────────────────────────────────────────────────

class SEOPayload(BaseModel):
    topic: Optional[str] = None


@router.post("/{project_id}/seo/generate", response_model=Dict[str, Any])
async def generate_project_seo(
    project_id: str,
    payload: Optional[SEOPayload] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """Generate SEO package: YouTube Title, Description, Tags, Caption & High-CTR Thumbnail via AI."""
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
        res = await asyncio.to_thread(provider.generate_json, prompt, system_prompt, max_tokens=400)
    except Exception as e:
        logger.warning(f"AI SEO generation failed: {e}")
        res = None

    if not res or not isinstance(res, dict) or not res.get("title"):
        clean = topic.strip().title()
        res = {
            "title": f"{clean} 🎶 Nursery Rhymes & Kids Songs | 3D Animation for Toddlers ✨",
            "description": f"Welcome to our magical world of preschool music and joyful discovery! 🌟\n\nSing, dance, and learn with cute 3D cartoon friends in this animated nursery rhyme about {clean}.\n\n🔔 Subscribe for weekly educational rhymes, phonics, and dance-along toddler cartoons!\n\n#nurseryrhymes #kidssongs #toddlerlearning #3danimation",
            "tags": f"{clean.lower()}, kids songs, nursery rhymes, toddler songs, preschool learning, 3d cartoon, rhymes for babies, baby learning, educational songs, sing along, cartoon for kids, bedtime lullaby, animation",
            "caption": f"Sing and dance along with {clean}! 🌟🎵 Learn, smile, and explore with our cute 3D cartoon friends! #kidssongs #nurseryrhymes #preschool #toddlerfun",
        }
    else:
        # Normalize fields in case LLM outputs lists or alternative keys
        clean = topic.strip().title()
        if not res.get("title"):
            res["title"] = f"{clean} 🎶 Nursery Rhymes & Kids Songs | 3D Animation for Toddlers ✨"
        
        tags_raw = res.get("tags") or res.get("keywords") or res.get("search_tags") or res.get("hashtags")
        if isinstance(tags_raw, list):
            res["tags"] = ", ".join(str(t).strip() for t in tags_raw if t)
        elif isinstance(tags_raw, str) and tags_raw.strip():
            res["tags"] = tags_raw.strip()
        else:
            res["tags"] = f"{clean.lower()}, kids songs, nursery rhymes, toddler songs, preschool learning, 3d cartoon"

        if not res.get("description"):
            res["description"] = f"Join our 3D animated preschool adventure with {clean}! Sing along, dance, and learn with colorful cartoon friends.\n\n🔔 Subscribe for more rhymes!"
        if not res.get("caption"):
            res["caption"] = f"Sing and learn with {clean}! 🌟 #nurseryrhymes #kidssongs #preschool"

    # Automatically generate High-CTR Thumbnail matching selected topic & SEO title
    project_dir = Path(str(settings.resolved_project_dir)) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = project_dir / "thumbnail.jpg"

    char_res = await session.execute(select(Character).where(Character.project_id == project_id))
    chars = char_res.scalars().all()
    char_name = chars[0].name if chars else "Hero"
    char_app = chars[0].appearance if chars else ""

    seo_title = res.get("title", project.title or topic)
    thumb_prompt = build_high_ctr_thumbnail_prompt(
        title=seo_title,
        topic=topic,
        character_name=char_name,
        appearance=char_app,
    )
    res["thumbnail_prompt"] = thumb_prompt

    try:
        await asyncio.to_thread(
            generate_high_ctr_thumbnail,
            title=seo_title,
            topic=topic,
            output_thumbnail_path=str(thumb_path),
            video_path=None,  # NEVER take from video frame
            aspect_ratio="16:9",
            character_name=char_name,
            character_appearance=char_app,
            custom_prompt=thumb_prompt,
        )
        res["thumbnail_url"] = f"/api/v1/projects/{project_id}/thumbnail"
    except Exception as e:
        logger.warning(f"Thumbnail auto-generation during SEO failed: {e}")

    meta = dict(project.metadata_json or {})
    meta["manual_seo"] = res
    meta["thumbnail_prompt"] = thumb_prompt
    project.metadata_json = meta
    await project_repo.update(project)
    await session.commit()
    return res


class GenerateThumbnailPayload(BaseModel):
    aspect_ratio: Optional[str] = "16:9"
    title: Optional[str] = None
    topic: Optional[str] = None
    prompt_override: Optional[str] = None


@router.post("/{project_id}/thumbnail/generate", response_model=Dict[str, Any])
async def generate_project_thumbnail(
    project_id: str,
    payload: Optional[GenerateThumbnailPayload] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """Generate or regenerate a High-CTR YouTube Kids Thumbnail for the project."""
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dir = Path(str(settings.resolved_project_dir)) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = project_dir / "thumbnail.jpg"

    meta = dict(project.metadata_json or {})
    seo = meta.get("manual_seo") or {}
    title = (payload and payload.title) or seo.get("title") or project.title or "Preschool Kids Song"
    topic = (payload and payload.topic) or project.topic or project.title or "Nursery Rhymes"
    ratio = (payload and payload.aspect_ratio) or "16:9"

    char_res = await session.execute(select(Character).where(Character.project_id == project_id))
    chars = char_res.scalars().all()
    char_name = chars[0].name if chars else "Hero"
    char_app = chars[0].appearance if chars else ""

    ai_prompt = (payload and payload.prompt_override) or build_high_ctr_thumbnail_prompt(
        title=title,
        topic=topic,
        character_name=char_name,
        appearance=char_app,
    )

    await asyncio.to_thread(
        generate_high_ctr_thumbnail,
        title=title,
        topic=topic,
        output_thumbnail_path=str(thumb_path),
        video_path=None,  # NEVER take from video frame
        aspect_ratio=ratio,
        character_name=char_name,
        character_appearance=char_app,
        custom_prompt=ai_prompt,
    )

    # Save prompt to companion text file for easy external copy
    prompt_file = project_dir / "thumbnail_prompt.txt"
    try:
        prompt_file.write_text(ai_prompt, encoding="utf-8")
    except Exception:
        pass

    # Save to Asset
    asset_res = await session.execute(select(Asset).where(Asset.project_id == project_id, Asset.asset_type == "thumbnail"))
    existing_asset = asset_res.scalars().first()
    if not existing_asset:
        session.add(Asset(project_id=project_id, asset_type="thumbnail", file_path=str(thumb_path)))
    else:
        existing_asset.file_path = str(thumb_path)

    meta["thumbnail_prompt"] = ai_prompt
    if "manual_seo" in meta and isinstance(meta["manual_seo"], dict):
        meta["manual_seo"]["thumbnail_prompt"] = ai_prompt
    project.metadata_json = meta
    await project_repo.update(project)
    await session.commit()

    return {
        "status": "success",
        "thumbnail_url": f"/api/v1/projects/{project_id}/thumbnail",
        "aspect_ratio": ratio,
        "thumbnail_prompt": ai_prompt,
        "message": "High-CTR YouTube Kids Thumbnail generated successfully!",
    }


@router.get("/{project_id}/thumbnail/prompt", response_model=Dict[str, Any])
async def get_project_thumbnail_prompt(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve the AI prompt used for generating the thumbnail background."""
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    seo = meta.get("manual_seo") or {}
    prompt = meta.get("thumbnail_prompt") or seo.get("thumbnail_prompt")

    project_dir = Path(str(settings.resolved_project_dir)) / project_id
    prompt_file = project_dir / "thumbnail_prompt.txt"
    if not prompt and prompt_file.exists():
        try:
            prompt = prompt_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass

    if not prompt:
        char_res = await session.execute(select(Character).where(Character.project_id == project_id))
        chars = char_res.scalars().all()
        char_name = chars[0].name if chars else "Hero"
        char_app = chars[0].appearance if chars else ""
        prompt = build_high_ctr_thumbnail_prompt(
            title=seo.get("title") or project.title or "Preschool Kids Song",
            topic=project.topic or project.title or "Nursery Rhymes",
            character_name=char_name,
            appearance=char_app,
        )

    return {"project_id": project_id, "prompt": prompt}


@router.get("/{project_id}/thumbnail")
async def get_project_thumbnail(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Serve the generated High-CTR thumbnail image. If missing, generates dynamically for the project on-the-fly."""
    thumb_path = Path(str(settings.resolved_project_dir)) / project_id / "thumbnail.jpg"
    if not thumb_path.exists():
        project_repo = ProjectRepository(session)
        project = await project_repo.get(project_id)
        if project:
            meta = project.metadata_json or {}
            seo = meta.get("manual_seo") or {}
            title = seo.get("title") or project.title or "Preschool Kids Song"
            topic = project.topic or project.title or "Nursery Rhymes"
            thumb_path.parent.mkdir(parents=True, exist_ok=True)

            char_res = await session.execute(select(Character).where(Character.project_id == project_id))
            chars = char_res.scalars().all()
            char_name = chars[0].name if chars else "Hero"
            char_app = chars[0].appearance if chars else ""

            ai_prompt = meta.get("thumbnail_prompt") or build_high_ctr_thumbnail_prompt(
                title=title,
                topic=topic,
                character_name=char_name,
                appearance=char_app,
            )

            await asyncio.to_thread(
                generate_high_ctr_thumbnail,
                title=title,
                topic=topic,
                output_thumbnail_path=str(thumb_path),
                video_path=None,  # NEVER take from video frame
                aspect_ratio="16:9",
                character_name=char_name,
                character_appearance=char_app,
                custom_prompt=ai_prompt,
            )
            if thumb_path.exists():
                return FileResponse(str(thumb_path), media_type="image/jpeg", filename="thumbnail.jpg")
        raise HTTPException(status_code=404, detail="Thumbnail not yet generated")
    return FileResponse(str(thumb_path), media_type="image/jpeg", filename="thumbnail.jpg")


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
            "description": f"Welcome to our magical world of preschool music and joyful discovery! 🌟\n\nSing, dance, and learn with cute 3D cartoon friends in this animated nursery rhyme about {clean}.\n\n🔔 Subscribe for weekly educational rhymes, phonics, and dance-along toddler cartoons!\n\n#nurseryrhymes #kidssongs #toddlerlearning #3danimation",
            "tags": f"{clean.lower()}, kids songs, nursery rhymes, toddler songs, preschool learning, 3d cartoon, rhymes for babies, baby learning, educational songs, sing along, cartoon for kids, bedtime lullaby, animation",
            "caption": f"Sing and dance along with {clean}! 🌟🎵 Learn, smile, and explore with our cute 3D cartoon friends! #kidssongs #nurseryrhymes #preschool #toddlerfun",
            "thumbnail_url": f"/api/v1/projects/{project_id}/thumbnail",
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
    uploaded = sum(1 for s in scenes if (s.uploaded_file and Path(s.uploaded_file).exists()) or s.prompt_status in ("VIDEO_UPLOADED", "ORDER_CONFIRMED"))
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
# Scene Video Upload & Intelligent AI / Semantic Prompt Matching Engine
# ─────────────────────────────────────────────────────────────────────────────

def _clean_filename_tokens(filename: str) -> List[str]:
    """Extract meaningful semantic keywords from video filename, removing noise, tech terms, and timestamps."""
    base = os.path.splitext(filename)[0]
    # Expand camelCase: DancingBaby -> Dancing Baby
    base = re.sub(r"([a-z])([A-Z])", r"\1 \2", base)
    # Strip numeric timestamps (e.g. 20260925195005 or long digit sequences >= 4)
    base = re.sub(r"\b\d{4,}\b", " ", base)
    # Replace non-alphanumeric with spaces
    base = re.sub(r"[^a-zA-Z0-9\s]", " ", base)
    # Filter common video generator noise words
    stop_words = {
        "mp4", "mov", "webm", "mkv", "avi", "video", "clip", "output", "render",
        "final", "upscale", "upscaled", "1080p", "720p", "4k", "2k", "60fps", "30fps",
        "fps", "hd", "hq", "v1", "v2", "v3", "runway", "gen2", "gen3", "kling",
        "luma", "pika", "hailuo", "minimax", "sora", "seed", "dreamina", "unresolved",
        "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "by",
        "of", "from", "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "but", "if", "then", "else", "when", "up", "out",
        "across", "into", "onto", "over", "under", "about", "scene", "shot"
    }
    tokens = [w.lower() for w in base.split() if len(w) > 1 and not w.isdigit() and w.lower() not in stop_words]
    return tokens


def _extract_scene_number_from_filename(filename: str, total_scenes: int) -> Optional[int]:
    """Accurate regex extraction for explicit scene numbers (avoiding fps/resolution false positives)."""
    name = os.path.splitext(filename)[0].lower()
    patterns = [
        r"(?:^|[_\-\s])scene[_\-\s]?0*(\d{1,3})(?:[_\-\s]|$)",
        r"(?:^|[_\-\s])shot[_\-\s]?0*(\d{1,3})(?:[_\-\s]|$)",
        r"(?:^|[_\-\s])s0*(\d{1,2})(?:[_\-\s]|$)",
        r"(?:^|[_\-\s])clip[_\-\s]?0*(\d{1,3})(?:[_\-\s]|$)",
        r"^0*(\d{1,2})[_\-\s]",  # Leading number like 01_dancing_baby
    ]
    for pat in patterns:
        m = re.search(pat, name)
        if m:
            try:
                n = int(m.group(1))
                if 1 <= n <= total_scenes:
                    return n
            except ValueError:
                pass
    return None


def _calculate_semantic_similarity(
    filename: str,
    scene: Scene,
    all_scenes: Optional[List[Scene]] = None,
) -> Tuple[float, str, List[str]]:
    """
    Compute local lexical & semantic overlap score between filename keywords and scene prompt/lyrics.
    Distinct entity tokens (characters, animals, specific actions) are weighted much higher than common project words.
    """
    tokens = _clean_filename_tokens(filename)
    if not tokens:
        return 0.0, "No descriptive tokens in filename", []

    prompt_text = (scene.video_prompt or "").lower()
    lyrics_text = (scene.lyrics or "").lower()
    dialogue_text = (scene.dialogue or "").lower()
    env_text = (scene.environment or "").lower()
    char_list = scene.characters or []
    char_text = " ".join([c.get("name", "") if isinstance(c, dict) else str(c) for c in char_list]).lower()
    action_list = scene.actions or []
    action_text = " ".join([str(a) for a in action_list]).lower()

    full_scene_corpus = f"{prompt_text} {lyrics_text} {dialogue_text} {env_text} {char_text} {action_text}"

    # Calculate token document frequency across all scenes to downweight ubiquitous words
    doc_freq = {}
    if all_scenes:
        for s in all_scenes:
            s_corp = f"{(s.video_prompt or '').lower()} {(s.lyrics or '').lower()} {(s.environment or '').lower()}"
            for tok in set(tokens):
                if tok in s_corp:
                    doc_freq[tok] = doc_freq.get(tok, 0) + 1

    score = 0.0
    matched_words = []
    num_scenes = len(all_scenes) if all_scenes else 1

    for token in tokens:
        df = doc_freq.get(token, 1)
        # Distinctiveness weight: if token appears in almost every scene (like 'cloud' in 'Cloud Critters'), reduce weight
        idf_mult = 1.0
        if num_scenes > 2:
            ratio = df / num_scenes
            if ratio > 0.6:
                idf_mult = 0.15  # Ubiquitous theme word
            elif ratio > 0.35:
                idf_mult = 0.4
            else:
                idf_mult = 1.5  # Highly specific keyword (e.g. 'frog', 'sheep', 'bunny', 'puppy')

        if token in char_text or token in action_text:
            score += 55.0 * idf_mult
            matched_words.append(token)
        elif token in lyrics_text:
            score += 45.0 * idf_mult
            matched_words.append(token)
        elif token in prompt_text:
            score += 35.0 * idf_mult
            matched_words.append(token)
        elif token in env_text:
            score += 20.0 * idf_mult
            matched_words.append(token)
        elif token in full_scene_corpus:
            score += 15.0 * idf_mult
            matched_words.append(token)

    # Multi-token phrase bonus (e.g., 'cloud rings' or 'floating hill' or 'bunny and puppy')
    combined_name = " ".join(tokens)
    if len(tokens) >= 2 and combined_name in full_scene_corpus:
        score += 35.0

    norm_score = min(100.0, score)
    if matched_words:
        reason = f"Keywords matched: '{', '.join(set(matched_words))}' with Scene {scene.scene_number} prompt/lyrics"
    else:
        reason = f"Low semantic match with Scene {scene.scene_number}"

    return norm_score, reason, matched_words


def _ai_match_filenames_to_scenes(
    scenes: List[Scene],
    video_filenames: List[str],
) -> Dict[str, Dict[str, Any]]:
    """Use AI Provider (Ollama / OpenRouter / Claude / OmniRoute) to semantically match video titles to scene prompts."""
    if not video_filenames or not scenes:
        return {}

    provider = get_ai_provider()

    scenes_desc = []
    occupied_nums = {s.scene_number for s in scenes if s.uploaded_file or s.prompt_status == "VIDEO_UPLOADED"}

    for s in scenes:
        prompt_snippet = (s.video_prompt or s.lyrics or s.environment or "")[:180].replace("\n", " ")
        dur_val = float(s.duration) if s.duration is not None else 8.0
        status_tag = "[OCCUPIED - Already Has Video]" if s.scene_number in occupied_nums else "[VACANT - Needs Video Clip]"
        scenes_desc.append(
            f"Scene {s.scene_number} {status_tag}: Visual Prompt: \"{prompt_snippet}\" | Lyrics: \"{s.lyrics or ''}\" | Duration: {dur_val:.1f}s"
        )
    scenes_str = "\n".join(scenes_desc)

    files_desc = "\n".join([f"{i+1}. {fn}" for i, fn in enumerate(video_filenames)])

    prompt = f"""You are an expert AI video editor. Match each uploaded video filename to the best scene number based on the scene's visual prompt, lyrics, characters, and actions.

RULES:
1. Every uploaded video filename MUST be matched to a UNIQUE scene number. Never assign two files to the same scene.
2. Prioritize VACANT scenes that need a video clip over occupied scenes.
3. Match specific subjects and actions (e.g. frog leaping -> frog scene, sheep sleeping -> sheep scene, puppy/bunny -> bunny/puppy scene).

AVAILABLE SCENES:
{scenes_str}

UPLOADED VIDEO FILENAMES:
{files_desc}

Output valid JSON only with this exact structure:
{{
  "matches": [
    {{
      "filename": "exact_filename.mp4",
      "scene_number": 1,
      "confidence": 95,
      "reason": "Explain how keywords/theme in filename match the visual prompt or lyrics of Scene 1"
    }}
  ]
}}
"""
    system_prompt = "You are a precise AI video editor assistant that accurately matches video clip filenames to story scenes with 1-to-1 unique mapping. Output strict JSON only."

    try:
        data = provider.generate_json(prompt, system_prompt=system_prompt)
        if data and isinstance(data, dict) and "matches" in data:
            results = {}
            for item in data.get("matches", []):
                fn = item.get("filename")
                s_num = item.get("scene_number")
                if fn and s_num is not None:
                    results[fn] = {
                        "scene_number": int(s_num),
                        "confidence": float(item.get("confidence", 85)),
                        "reason": str(item.get("reason", "AI matched to scene prompt")),
                    }
            return results
    except Exception as e:
        logger.warning(f"AI video filename matching failed: {e}")
    return {}


def _match_video_files_to_scenes(
    scenes: List[Scene],
    video_filenames: List[str],
) -> Dict[str, Dict[str, Any]]:
    """
    Combined Hybrid Matcher with 1-to-1 Unique Scene Assignment:
    1. Explicit scene number regex (98% confidence)
    2. AI LLM Prompt & Lyrics Matcher
    3. NLP / Semantic keyword overlap scoring (with Vacancy preference)
    4. Global bipartite conflict resolver to guarantee NO duplicate scene assignments.
    """
    total = len(scenes)
    scenes_by_num = {s.scene_number: s for s in scenes}
    occupied_nums = {s.scene_number for s in scenes if s.uploaded_file or s.prompt_status == "VIDEO_UPLOADED"}

    # Step 1: Query AI Provider for semantic suggestions
    ai_matches = {}
    try:
        ai_matches = _ai_match_filenames_to_scenes(scenes, video_filenames)
    except Exception as e:
        logger.warning(f"AI matcher exception: {e}")

    # Step 2: Build complete candidate score matrix for all (filename, scene) pairs
    candidates = []
    explicit_assigned = {}

    for fn in video_filenames:
        explicit_num = _extract_scene_number_from_filename(fn, total)
        if explicit_num and explicit_num in scenes_by_num:
            explicit_assigned[fn] = {
                "scene_number": explicit_num,
                "confidence": 98.0,
                "reason": f"Explicit scene identifier 'Scene {explicit_num}' detected in filename",
                "source": "explicit_pattern",
            }
            continue

        ai_match = ai_matches.get(fn)

        for s in scenes:
            s_score, s_reason, _ = _calculate_semantic_similarity(fn, s, scenes)
            source = "semantic_keywords"

            if ai_match and ai_match["scene_number"] == s.scene_number:
                # Strong AI consensus
                ai_conf = ai_match["confidence"]
                s_score = max(s_score, ai_conf) + 15.0
                s_reason = f"AI Match ({int(ai_conf)}%): {ai_match['reason']}"
                source = "ai"

            # Vacancy bonus: if scene is currently unassigned/vacant, give priority
            if s.scene_number not in occupied_nums:
                s_score += 25.0

            candidates.append((s_score, fn, s.scene_number, s_reason, source))

    # Sort all candidates by score descending
    candidates.sort(key=lambda x: x[0], reverse=True)

    # Step 3: Global Greedy 1-to-1 Assignment (Conflict Resolver)
    final_matches = dict(explicit_assigned)
    assigned_files = set(final_matches.keys())
    assigned_scenes = {info["scene_number"] for info in final_matches.values()}

    for score, fn, s_num, reason, source in candidates:
        if fn in assigned_files:
            continue
        # Avoid assigning to a scene already claimed by another file in this batch
        if s_num in assigned_scenes:
            continue

        final_matches[fn] = {
            "scene_number": s_num,
            "confidence": min(98.0, round(score, 1)),
            "reason": reason or f"Matched to Scene {s_num}",
            "source": source,
        }
        assigned_files.add(fn)
        assigned_scenes.add(s_num)

    # Step 4: Fallback for any remaining unassigned files
    remaining_files = [fn for fn in video_filenames if fn not in final_matches]
    if remaining_files:
        available_scenes = [
            s.scene_number for s in scenes
            if s.scene_number not in assigned_scenes and s.scene_number not in occupied_nums
        ]
        if not available_scenes:
            available_scenes = [s.scene_number for s in scenes if s.scene_number not in assigned_scenes]
        if not available_scenes:
            available_scenes = [s.scene_number for s in scenes]

        for i, fn in enumerate(remaining_files):
            target_s = available_scenes[i % len(available_scenes)]
            final_matches[fn] = {
                "scene_number": target_s,
                "confidence": 35.0,
                "reason": f"Allocated to Scene {target_s}",
                "source": "sequential_fallback",
            }

    return final_matches


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
    Batch-upload multiple scene videos with AI & Semantic Prompt Matching.
    Matches uploaded video titles/filenames to scene prompts and lyrics.
    Auto-maps high-confidence matches; stores unresolved clips for user confirmation.
    """
    result_list = await session.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc())
    )
    scenes = result_list.scalars().all()
    scenes_by_num = {s.scene_number: s for s in scenes}

    project_dir = Path(str(settings.resolved_project_dir)) / project_id / "uploaded_scenes"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Read contents and collect valid filenames
    file_data = []
    valid_filenames = []
    results = []
    unresolved = []

    for file in files:
        filename = file.filename or "unknown.mp4"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in {".mp4", ".mov", ".webm"}:
            results.append({"filename": filename, "status": "REJECTED", "reason": "Unsupported file type"})
            continue
        content = await file.read()
        file_data.append((filename, ext, content))
        valid_filenames.append(filename)

    # Run AI & Semantic Matcher
    matches = await asyncio.to_thread(_match_video_files_to_scenes, scenes, valid_filenames)

    # Process uploads
    for filename, ext, content in file_data:
        match_info = matches.get(filename, {
            "scene_number": 1,
            "confidence": 30.0,
            "reason": "Default assignment",
            "source": "fallback"
        })
        scene_num = match_info["scene_number"]
        confidence = match_info.get("confidence", 50.0)
        match_reason = match_info.get("reason", "")
        match_source = match_info.get("source", "semantic")

        # Auto-map if confidence >= 50 or explicit pattern and scene exists
        if scene_num in scenes_by_num and confidence >= 50.0:
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
                "confidence": confidence,
                "match_reason": match_reason,
                "match_source": match_source,
                "duration": duration,
            })
        else:
            # Save as temporary unresolved file with AI suggestion
            tmp_path = project_dir / f"unresolved_{filename}"
            tmp_path.write_bytes(content)
            duration = await asyncio.to_thread(_probe_video_duration, str(tmp_path))
            unresolved.append({
                "filename": filename,
                "tmp_path": str(tmp_path),
                "duration": duration,
                "suggested_scene_number": scene_num,
                "confidence": confidence,
                "match_reason": match_reason,
                "match_source": match_source,
            })
            results.append({
                "filename": filename,
                "status": "NEEDS_ASSIGNMENT",
                "suggested_scene_number": scene_num,
                "confidence": confidence,
                "match_reason": match_reason,
            })

    await session.commit()
    return {
        "results": results,
        "unresolved": unresolved,
        "total_uploaded": sum(1 for r in results if r["status"] == "UPLOADED"),
        "needs_assignment": len(unresolved),
    }


@router.post("/{project_id}/scenes/ai-match-videos", response_model=Dict[str, Any])
async def ai_match_unresolved_videos(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Run AI & Semantic Prompt Matching on all unresolved uploaded videos.
    Returns AI suggestions, confidence scores, and reasons comparing video titles to scene prompts.
    """
    result_list = await session.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc())
    )
    scenes = result_list.scalars().all()
    if not scenes:
        raise HTTPException(status_code=404, detail="No scenes found for project")

    project_dir = Path(str(settings.resolved_project_dir)) / project_id / "uploaded_scenes"
    if not project_dir.exists():
        return {"matches": [], "unresolved_count": 0}

    unresolved_files = list(project_dir.glob("unresolved_*"))
    if not unresolved_files:
        return {"matches": [], "unresolved_count": 0}

    filenames = [f.name.replace("unresolved_", "") for f in unresolved_files]
    fn_to_path = {f.name.replace("unresolved_", ""): str(f) for f in unresolved_files}

    matches = await asyncio.to_thread(_match_video_files_to_scenes, scenes, filenames)

    scenes_by_num = {s.scene_number: s for s in scenes}
    match_list = []
    for fn in filenames:
        info = matches.get(fn, {})
        s_num = info.get("scene_number", 1)
        matched_scene = scenes_by_num.get(s_num)
        match_list.append({
            "filename": fn,
            "tmp_path": fn_to_path.get(fn),
            "suggested_scene_number": s_num,
            "confidence": info.get("confidence", 50.0),
            "match_reason": info.get("reason", ""),
            "match_source": info.get("source", "semantic"),
            "scene_prompt_preview": (matched_scene.video_prompt or "")[:120] if matched_scene else "",
            "scene_lyrics_preview": matched_scene.lyrics if matched_scene else "",
        })

    return {
        "matches": match_list,
        "unresolved_count": len(unresolved_files),
        "total_scenes": len(scenes),
    }


class SmartAssignPayload(BaseModel):
    assignments: Optional[List[Dict[str, Any]]] = None  # List of {"tmp_path": "...", "scene_number": 1}


@router.post("/{project_id}/scenes/auto-assign-smart", response_model=Dict[str, Any])
async def auto_assign_smart(
    project_id: str,
    payload: Optional[SmartAssignPayload] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Apply AI-matched scene assignments to unresolved video files in one click.
    If no assignments provided in payload, automatically computes best AI matching.
    """
    result_list = await session.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number.asc())
    )
    scenes = result_list.scalars().all()
    scenes_by_num = {s.scene_number: s for s in scenes}

    project_dir = Path(str(settings.resolved_project_dir)) / project_id / "uploaded_scenes"
    project_dir.mkdir(parents=True, exist_ok=True)

    assignments_to_apply = []
    if payload and payload.assignments:
        assignments_to_apply = payload.assignments
    else:
        # Auto-compute matches for all unresolved files in directory
        unresolved_files = list(project_dir.glob("unresolved_*"))
        filenames = [f.name.replace("unresolved_", "") for f in unresolved_files]
        fn_to_path = {f.name.replace("unresolved_", ""): str(f) for f in unresolved_files}
        matches = await asyncio.to_thread(_match_video_files_to_scenes, scenes, filenames)

        for fn in filenames:
            info = matches.get(fn, {})
            assignments_to_apply.append({
                "tmp_path": fn_to_path.get(fn),
                "scene_number": info.get("scene_number", 1),
                "reason": info.get("reason", ""),
            })

    assigned_count = 0
    assigned_details = []

    for item in assignments_to_apply:
        tmp_path = item.get("tmp_path")
        scene_num = int(item.get("scene_number", 1))
        if not tmp_path or not Path(tmp_path).exists():
            continue

        scene = scenes_by_num.get(scene_num)
        if not scene:
            continue

        ext = os.path.splitext(tmp_path)[1].lower() or ".mp4"
        dest = project_dir / f"scene_{scene_num:03d}{ext}"
        try:
            # Move tmp file to destination
            Path(tmp_path).rename(dest)
        except Exception:
            shutil.copy2(tmp_path, dest)
            try:
                Path(tmp_path).unlink()
            except Exception:
                pass

        duration = await asyncio.to_thread(_probe_video_duration, str(dest))
        scene.uploaded_file = str(dest)
        scene.uploaded_duration = duration
        scene.prompt_status = "VIDEO_UPLOADED"
        scene.local_video_path = str(dest)
        scene.render_path = str(dest)
        scene.status = "COMPLETED"
        scene.generation_status = "UPLOADED"
        scene.scene_order = scene.scene_number
        await session.flush()

        assigned_count += 1
        assigned_details.append({
            "scene_number": scene_num,
            "filename": os.path.basename(dest),
            "duration": duration,
            "reason": item.get("reason", "Assigned via Smart AI Prompt Matcher"),
        })

    await session.commit()
    return {
        "status": "success",
        "assigned_count": assigned_count,
        "details": assigned_details,
        "message": f"Successfully matched and assigned {assigned_count} scenes using AI & Prompt analysis.",
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
    scene.scene_order = scene.scene_order if scene.scene_order is not None else scene.scene_number
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

    # Check audio robustly (master_soundtrack.wav, song.mp3, song.wav, etc.)
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
    audio_ok = bool(audio_file)

    # Check SRT
    srt_path = project_dir / "subtitles.srt"
    alt_srt = project_dir / "audio" / "lyrics.srt"
    alt_srt2 = project_dir / "audio" / "subtitles.srt"
    srt_ok = srt_path.exists() or alt_srt.exists() or alt_srt2.exists()

    # Check scenes & auto-heal if physical video files exist on disk
    uploaded_scenes_dir = project_dir / "uploaded_scenes"
    db_healed = False
    if uploaded_scenes_dir.exists():
        for s in scenes:
            if not (s.uploaded_file and Path(s.uploaded_file).exists()):
                candidates = [
                    uploaded_scenes_dir / f"scene_{s.scene_number:03d}.mp4",
                    uploaded_scenes_dir / f"scene_{s.scene_number:02d}.mp4",
                    uploaded_scenes_dir / f"scene_{s.scene_number}.mp4",
                    uploaded_scenes_dir / f"scene_{s.scene_number:03d}.mov",
                    uploaded_scenes_dir / f"scene_{s.scene_number:02d}.mov",
                    uploaded_scenes_dir / f"scene_{s.scene_number}.mov",
                    uploaded_scenes_dir / f"scene_{s.scene_number:03d}.webm",
                    uploaded_scenes_dir / f"scene_{s.scene_number:02d}.webm",
                    uploaded_scenes_dir / f"scene_{s.scene_number}.webm",
                ]
                for cand in candidates:
                    if cand.exists():
                        s.uploaded_file = str(cand)
                        try:
                            s.uploaded_duration = _probe_video_duration(str(cand))
                        except Exception:
                            pass
                        s.prompt_status = "VIDEO_UPLOADED"
                        db_healed = True
                        break
        if db_healed:
            await session.commit()

    total = len(scenes)
    uploaded = [s for s in scenes if s.uploaded_file and Path(s.uploaded_file).exists()]
    missing = [s.scene_number for s in scenes if not (s.uploaded_file and Path(s.uploaded_file).exists())]

    # Check if final video is already assembled
    final_v1 = project_dir / "output" / "final_video.mp4"
    final_v2 = project_dir / "final.mp4"
    final_video_file = None
    if final_v1.exists():
        final_video_file = str(final_v1)
    elif final_v2.exists():
        final_video_file = str(final_v2)
    elif meta.get("final_video_path") and Path(meta.get("final_video_path")).exists():
        final_video_file = meta.get("final_video_path")

    final_video_duration = 0.0
    if final_video_file:
        try:
            final_video_duration = _probe_video_duration(final_video_file)
        except Exception:
            final_video_duration = 0.0

    # Check unresolved files waiting in uploaded_scenes directory
    unresolved_dir = project_dir / "uploaded_scenes"
    unresolved_count = 0
    if unresolved_dir.exists():
        unresolved_count = len(list(unresolved_dir.glob("unresolved_*")))

    # Upload details per scene
    scene_details = []
    for s in scenes:
        has_file = bool(s.uploaded_file and Path(s.uploaded_file).exists())
        fn = Path(s.uploaded_file).name if has_file else None
        sz = None
        if has_file:
            try:
                sz = Path(s.uploaded_file).stat().st_size
            except Exception:
                sz = None

        scene_details.append({
            "scene_id": s.id,
            "scene_number": s.scene_number,
            "has_video": has_file,
            "filename": fn,
            "file_path": s.uploaded_file if has_file else None,
            "duration": s.duration or 0.0,
            "uploaded_duration": s.uploaded_duration,
            "file_size": sz,
            "prompt_status": s.prompt_status,
        })

    confirmed_count = sum(1 for s in scenes if s.prompt_status == "ORDER_CONFIRMED")
    ready = (total > 0 and len(missing) == 0 and audio_ok)
    thumb_prompt = meta.get("thumbnail_prompt") or meta.get("manual_seo", {}).get("thumbnail_prompt")
    if not thumb_prompt:
        prompt_file = project_dir / "thumbnail_prompt.txt"
        if prompt_file.exists():
            try:
                thumb_prompt = prompt_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass

    return {
        "ready": ready,
        "total_scenes": total,
        "uploaded_scenes": len(uploaded),
        "missing_scenes": missing,
        "audio_available": audio_ok,
        "audio_file": audio_file,
        "srt_available": srt_ok,
        "sequence_confirmed": (confirmed_count == total and total > 0) or ready,
        "topic": project.topic,
        "title": project.title,
        "final_video_exists": bool(final_video_file),
        "final_video_url": f"/api/v1/projects/{project_id}/assembly/final-video" if final_video_file else None,
        "final_video_duration": final_video_duration,
        "thumbnail_url": f"/api/v1/projects/{project_id}/thumbnail",
        "thumbnail_prompt": thumb_prompt,
        "unresolved_count": unresolved_count,
        "scene_details": scene_details,
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

    # Check scenes & auto-heal if physical video files exist on disk
    uploaded_scenes_dir = project_dir / "uploaded_scenes"
    db_healed = False
    if uploaded_scenes_dir.exists():
        for s in scenes:
            if not (s.uploaded_file and Path(s.uploaded_file).exists()):
                candidates = [
                    uploaded_scenes_dir / f"scene_{s.scene_number:03d}.mp4",
                    uploaded_scenes_dir / f"scene_{s.scene_number:02d}.mp4",
                    uploaded_scenes_dir / f"scene_{s.scene_number}.mp4",
                    uploaded_scenes_dir / f"scene_{s.scene_number:03d}.mov",
                    uploaded_scenes_dir / f"scene_{s.scene_number:02d}.mov",
                    uploaded_scenes_dir / f"scene_{s.scene_number}.mov",
                    uploaded_scenes_dir / f"scene_{s.scene_number:03d}.webm",
                    uploaded_scenes_dir / f"scene_{s.scene_number:02d}.webm",
                    uploaded_scenes_dir / f"scene_{s.scene_number}.webm",
                ]
                for cand in candidates:
                    if cand.exists():
                        s.uploaded_file = str(cand)
                        try:
                            s.uploaded_duration = _probe_video_duration(str(cand))
                        except Exception:
                            pass
                        s.prompt_status = "VIDEO_UPLOADED"
                        db_healed = True
                        break
        if db_healed:
            await session.commit()

    if not scenes:
        raise HTTPException(
            status_code=400,
            detail="Assembly Validation Error: No storyboard scenes found for this project. Please create or generate scenes first."
        )

    # Validate all scene videos exist
    missing = [
        s.scene_number for s in scenes
        if not (s.uploaded_file and Path(s.uploaded_file).exists())
    ]
    if missing:
        missing_str = ", ".join(f"Scene {n}" for n in missing)
        raise HTTPException(
            status_code=400,
            detail=f"Assembly Validation Error: Missing video files for {len(missing)} scene(s) ({missing_str}). All {len(scenes)} scenes must have uploaded video clips before assembling."
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

        # Regenerate High-CTR Thumbnail with AI thematic background (NEVER from video frame)
        thumb_path = project_dir / "thumbnail.jpg"
        meta = dict(project.metadata_json or {})
        seo = meta.get("manual_seo") or {}
        title = seo.get("title") or project.title or project.topic or "Preschool Kids Video"
        topic = project.topic or project.title or "Nursery Rhymes"

        char_res = await session.execute(select(Character).where(Character.project_id == project_id))
        chars = char_res.scalars().all()
        char_name = chars[0].name if chars else "Hero"
        char_app = chars[0].appearance if chars else ""

        ai_prompt = meta.get("thumbnail_prompt") or build_high_ctr_thumbnail_prompt(
            title=title,
            topic=topic,
            character_name=char_name,
            appearance=char_app,
        )

        try:
            await asyncio.to_thread(
                generate_high_ctr_thumbnail,
                title=title,
                topic=topic,
                output_thumbnail_path=str(thumb_path),
                video_path=None,  # NEVER take from video frame!
                aspect_ratio="16:9",
                character_name=char_name,
                character_appearance=char_app,
                custom_prompt=ai_prompt,
            )
            # Update asset record
            asset_res = await session.execute(select(Asset).where(Asset.project_id == project_id, Asset.asset_type == "thumbnail"))
            existing_asset = asset_res.scalars().first()
            if not existing_asset:
                session.add(Asset(project_id=project_id, asset_type="thumbnail", file_path=str(thumb_path)))
            else:
                existing_asset.file_path = str(thumb_path)

            meta["thumbnail_prompt"] = ai_prompt
            project.metadata_json = meta
            await project_repo.update(project)
        except Exception as te:
            logger.warning(f"Thumbnail regeneration after video assembly failed: {te}")

        # Sync to root project final.mp4 so all players / endpoints find it
        legacy_final = project_dir / "final.mp4"
        try:
            shutil.copy2(str(final_path), str(legacy_final))
        except Exception:
            pass

        # Update project status to READY
        project.status = "READY"
        meta["final_video_path"] = str(final_path)
        meta["thumbnail_path"] = str(thumb_path)
        project.metadata_json = meta
        await project_repo.update(project)
        await session.commit()

        return {
            "status": "completed",
            "final_video": str(final_path),
            "thumbnail_url": f"/api/v1/projects/{project_id}/thumbnail",
            "duration": duration,
            "message": "Final video assembled and High-CTR Thumbnail generated successfully!",
        }
    except Exception as e:
        logger.error(f"Final video assembly failed for {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Assembly failed: {str(e)}")


def _has_audio_stream(file_path: str) -> bool:
    """Check if a video/audio file contains an audio stream."""
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", file_path]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return "audio" in res.stdout.lower()
    except Exception:
        return False


def _assemble_final_video(
    scene_video_paths: List[Path],
    audio_file: Optional[str],
    srt_file: Optional[str],
    output_path: Path,
) -> Path:
    """
    Advanced Video Compositor:
    1. Multi-Track Audio Mixing: Preserves scene clip audio/SFX and mixes with master Suno song audio.
    2. Intro & Outro Stems: Prepends intro clip & appends outro clip (song only plays during scenes).
    3. Channel Watermark Logo: Overlays channel badge in the bottom-right corner.
    4. Synchronized Subtitles: Burns clean white bold SRT lyrics with drop shadow.
    """
    import tempfile
    from app.api.v1.settings_api import get_db_config, ASSETS_DIR

    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg" or "/usr/local/bin/ffmpeg" or "ffmpeg"
    work_dir = output_path.parent
    work_dir.mkdir(parents=True, exist_ok=True)

    # Read compositing preferences from database
    scene_vol = float(get_db_config("SCENE_AUDIO_VOLUME", "0.70"))
    song_vol = float(get_db_config("SONG_AUDIO_VOLUME", "1.00"))
    burn_subs = get_db_config("BURN_SUBTITLES", "true").lower() in ("true", "1", "yes")

    logo_path = get_db_config("CHANNEL_LOGO_PATH", str(ASSETS_DIR / "channel_logo.png"))
    logo_enabled = get_db_config("CHANNEL_LOGO_ENABLED", "true").lower() in ("true", "1", "yes")
    has_logo = logo_enabled and os.path.exists(logo_path) and os.path.getsize(logo_path) > 100

    intro_path = get_db_config("INTRO_CLIP_PATH", str(ASSETS_DIR / "intro_clip.mp4"))
    intro_enabled = get_db_config("INTRO_ENABLED", "true").lower() in ("true", "1", "yes")
    has_intro = intro_enabled and os.path.exists(intro_path) and os.path.getsize(intro_path) > 1000

    outro_path = get_db_config("OUTRO_CLIP_PATH", str(ASSETS_DIR / "outro_clip.mp4"))
    outro_enabled = get_db_config("OUTRO_ENABLED", "true").lower() in ("true", "1", "yes")
    has_outro = outro_enabled and os.path.exists(outro_path) and os.path.getsize(outro_path) > 1000

    temp_files_to_clean = []

    # ── STEP 1: Normalize all scene clips to standard 1080p yuv420p + AAC stereo ──
    normalized_scenes = []
    has_any_scene_audio = False

    for idx, p in enumerate(scene_video_paths):
        norm_p = work_dir / f"norm_scene_{idx:03d}.mp4"
        temp_files_to_clean.append(norm_p)
        has_audio = _has_audio_stream(str(p))
        if has_audio:
            has_any_scene_audio = True
            norm_cmd = [
                ffmpeg_bin, "-y",
                "-i", str(p),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
                str(norm_p)
            ]
        else:
            # Generate silent audio track for clips without audio so concat filter works uniformly
            norm_cmd = [
                ffmpeg_bin, "-y",
                "-i", str(p),
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-shortest",
                str(norm_p)
            ]
        subprocess.run(norm_cmd, check=True, capture_output=True, text=True, timeout=300)
        normalized_scenes.append(norm_p)

    # ── STEP 2: Concat scene clips into continuous scene body (Stream copy for instantaneous concat) ──
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for np in normalized_scenes:
            f.write(f"file '{str(np)}'\n")
        concat_txt = f.name
    temp_files_to_clean.append(Path(concat_txt))

    scenes_body_raw = work_dir / "scenes_body_raw.mp4"
    temp_files_to_clean.append(scenes_body_raw)

    concat_cmd = [
        ffmpeg_bin, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        str(scenes_body_raw)
    ]
    res_cat = subprocess.run(concat_cmd, capture_output=True, text=True, timeout=120)
    if res_cat.returncode != 0:
        # Fallback to re-encode if stream copy fails
        re_concat = [
            ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", str(scenes_body_raw)
        ]
        subprocess.run(re_concat, check=True, capture_output=True, text=True, timeout=300)

    # ── STEP 3: Multi-Track Audio Mixing (Scene SFX + Song Track) & Subtitles ──
    scenes_body_mixed = work_dir / "scenes_body_mixed.mp4"
    temp_files_to_clean.append(scenes_body_mixed)

    has_srt = bool(srt_file and Path(srt_file).exists())
    has_song = bool(audio_file and Path(audio_file).exists())

    # Try burning subtitles using libass filter; if unavailable on system, embed as mov_text
    sub_filter = ""
    if burn_subs and has_srt:
        escaped_srt = str(srt_file).replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
        sub_filter = f"subtitles='{escaped_srt}':force_style='FontName=Arial,FontSize=24,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2.5,Shadow=1.5,MarginV=36,Alignment=2'"

    mixed_success = False

    if has_song and has_any_scene_audio:
        # Mix scene SFX audio + master song track
        filter_parts = []
        if sub_filter:
            filter_parts.append(f"[0:v]{sub_filter}[v_out]")
        else:
            filter_parts.append("[0:v]null[v_out]")

        filter_parts.append(f"[0:a]volume={scene_vol:.2f}[a_sfx]")
        filter_parts.append(f"[1:a]volume={song_vol:.2f}[a_song]")
        filter_parts.append("[a_sfx][a_song]amix=inputs=2:duration=first:dropout_transition=2[a_out]")

        filter_complex = ";".join(filter_parts)

        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(scenes_body_raw),
            "-i", str(audio_file),
            "-filter_complex", filter_complex,
            "-map", "[v_out]", "-map", "[a_out]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(scenes_body_mixed)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if res.returncode == 0 and os.path.exists(str(scenes_body_mixed)):
            mixed_success = True
        else:
            # Subtitle filter may have failed due to libass missing in ffmpeg build — retry audio mix without sub_filter
            no_sub_filter = f"[0:a]volume={scene_vol:.2f}[a_sfx];[1:a]volume={song_vol:.2f}[a_song];[a_sfx][a_song]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
            retry_cmd = [
                ffmpeg_bin, "-y",
                "-i", str(scenes_body_raw),
                "-i", str(audio_file),
                "-filter_complex", no_sub_filter,
                "-map", "0:v:0", "-map", "[a_out]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(scenes_body_mixed)
            ]
            res_retry = subprocess.run(retry_cmd, capture_output=True, text=True, timeout=300)
            if res_retry.returncode == 0:
                mixed_success = True

    if not mixed_success and has_song:
        # Song track overlay
        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(scenes_body_raw),
            "-i", str(audio_file),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(scenes_body_mixed)
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
        mixed_success = True

    if not mixed_success:
        # Fallback to scenes body raw
        shutil.copy2(str(scenes_body_raw), str(scenes_body_mixed))

    # ── STEP 4: Prepend Intro & Append Outro (with Inbuilt Audio preserved) ──
    clips_to_stitch = []

    if has_intro:
        norm_intro = work_dir / "norm_intro.mp4"
        temp_files_to_clean.append(norm_intro)
        intro_has_a = _has_audio_stream(intro_path)
        if intro_has_a:
            i_cmd = [
                ffmpeg_bin, "-y", "-i", intro_path,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
                str(norm_intro)
            ]
        else:
            i_cmd = [
                ffmpeg_bin, "-y", "-i", intro_path,
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-shortest",
                str(norm_intro)
            ]
        subprocess.run(i_cmd, check=True, capture_output=True, text=True, timeout=180)
        clips_to_stitch.append(norm_intro)

    clips_to_stitch.append(scenes_body_mixed)

    if has_outro:
        norm_outro = work_dir / "norm_outro.mp4"
        temp_files_to_clean.append(norm_outro)
        outro_has_a = _has_audio_stream(outro_path)
        if outro_has_a:
            o_cmd = [
                ffmpeg_bin, "-y", "-i", outro_path,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
                str(norm_outro)
            ]
        else:
            o_cmd = [
                ffmpeg_bin, "-y", "-i", outro_path,
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-shortest",
                str(norm_outro)
            ]
        subprocess.run(o_cmd, check=True, capture_output=True, text=True, timeout=180)
        clips_to_stitch.append(norm_outro)

    stitched_video = work_dir / "stitched_video.mp4"
    temp_files_to_clean.append(stitched_video)

    if len(clips_to_stitch) > 1:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for c in clips_to_stitch:
                f.write(f"file '{str(c)}'\n")
            full_concat_txt = f.name
        temp_files_to_clean.append(Path(full_concat_txt))

        s_cmd = [
            ffmpeg_bin, "-y",
            "-f", "concat", "-safe", "0",
            "-i", full_concat_txt,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            str(stitched_video)
        ]
        subprocess.run(s_cmd, check=True, capture_output=True, text=True, timeout=300)
    else:
        shutil.copy2(str(scenes_body_mixed), str(stitched_video))

    # ── STEP 5: Channel Watermark Logo Overlay (Bottom-Right Badge) ──
    if has_logo:
        logo_scale = int(get_db_config("CHANNEL_LOGO_SCALE", "180"))
        logo_opacity = float(get_db_config("CHANNEL_LOGO_OPACITY", "0.95"))
        logo_pos = get_db_config("CHANNEL_LOGO_POSITION", "bottom_right").lower()
        logo_bottom_spacing = int(get_db_config("CHANNEL_LOGO_BOTTOM_SPACING", "24"))

        if "top_right" in logo_pos:
            overlay_coord = f"W-w-24:{logo_bottom_spacing}"
        elif "bottom_left" in logo_pos:
            overlay_coord = f"24:H-h-{logo_bottom_spacing}"
        elif "top_left" in logo_pos:
            overlay_coord = f"24:{logo_bottom_spacing}"
        else:
            # Default Bottom Right (as shown in reference images)
            overlay_coord = f"W-w-24:H-h-{logo_bottom_spacing}"

        logo_cmd = [
            ffmpeg_bin, "-y",
            "-i", str(stitched_video),
            "-i", logo_path,
            "-filter_complex", f"[1:v]scale={logo_scale}:-1,format=rgba,colorchannelmixer=aa={logo_opacity:.2f}[logo];[0:v][logo]overlay={overlay_coord}[v_branded]",
            "-map", "[v_branded]", "-map", "0:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            "-movflags", "+faststart",
            str(output_path)
        ]
        res_logo = subprocess.run(logo_cmd, capture_output=True, text=True, timeout=300)
        if res_logo.returncode != 0:
            shutil.copy2(str(stitched_video), str(output_path))
    else:
        # Direct faststart finalization
        final_cmd = [
            ffmpeg_bin, "-y",
            "-i", str(stitched_video),
            "-c:v", "copy", "-c:a", "copy",
            "-movflags", "+faststart",
            str(output_path)
        ]
        res_fin = subprocess.run(final_cmd, capture_output=True, text=True, timeout=120)
        if res_fin.returncode != 0:
            shutil.copy2(str(stitched_video), str(output_path))

    # Clean up temporary scratch files
    for tf in temp_files_to_clean:
        try:
            if tf.exists():
                tf.unlink()
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
        # Try default locations
        cand1 = Path(str(settings.resolved_project_dir)) / project_id / "output" / "final_video.mp4"
        cand2 = Path(str(settings.resolved_project_dir)) / project_id / "final.mp4"
        if cand1.exists():
            video_path = str(cand1)
        elif cand2.exists():
            video_path = str(cand2)
        else:
            raise HTTPException(status_code=404, detail="Final video not yet assembled")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        content_disposition_type="inline",
        filename=f"final_video_{project_id[:8]}.mp4",
    )
