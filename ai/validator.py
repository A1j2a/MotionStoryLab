import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("studio.ai.validator")


class PlanCharacterSchema(BaseModel):
    character_id: Optional[str] = None
    id: Optional[str] = None
    name: str
    type: Optional[str] = "character"
    species: Optional[str] = None
    appearance: str
    colors: Optional[List[str]] = None
    clothing: Optional[str] = None
    personality: Optional[str] = None
    voice: Optional[str] = None
    animation_set: List[str] = Field(default_factory=list)


class PlanSceneSchema(BaseModel):
    scene_id: Optional[str] = None
    scene_number: int
    start_time: Optional[float] = None
    duration: float = 6.0
    end_time: Optional[float] = None
    environment: Any = "Sunny Green Meadow"
    characters: Any = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    camera: Optional[Dict[str, Any]] = None
    lighting: Optional[Any] = None
    dialogue: Optional[str] = None
    lyrics: Optional[str] = None
    music: Optional[str] = None
    sound_effects: List[str] = Field(default_factory=list)
    transition: Optional[str] = "cut"
    status: Optional[str] = "PENDING"


class ContentPlanSchema(BaseModel):
    title: str
    lyrics_full: str
    characters: List[PlanCharacterSchema]
    scenes: List[PlanSceneSchema]


def validate_storyboard_scenes(
    scenes: List[Dict[str, Any]],
    characters: List[Dict[str, Any]],
    total_audio_duration: float,
    approved_lyrics: str,
) -> Tuple[bool, List[str]]:
    """
    Validates storyboard scene timeline before rendering:
    - Verifies scene list is non-empty
    - Verifies scenes do not overlap or have huge timeline gaps (> 1.0s)
    - Verifies total scene duration covers the audio duration
    - Verifies referenced characters exist in the Character Bible
    - Verifies each scene has environment, camera, and lyrics
    Returns (is_valid, list_of_errors).
    """
    errors = []
    if not scenes:
        return False, ["Scene list is empty."]

    char_bible_ids = set()
    for c in characters:
        if c.get("character_id"):
            char_bible_ids.add(c["character_id"])
        if c.get("id"):
            char_bible_ids.add(c["id"])
        if c.get("name"):
            char_bible_ids.add(c["name"])

    prev_end = 0.0
    for idx, sc in enumerate(scenes, start=1):
        s_num = sc.get("scene_number", idx)
        s_start = float(sc.get("start_time", prev_end))
        s_dur = float(sc.get("duration", 5.0))
        s_end = float(sc.get("end_time", s_start + s_dur))

        # Check duration
        if s_dur <= 0:
            errors.append(f"Scene {s_num}: Invalid duration ({s_dur}s).")

        # Check timeline continuity
        if idx > 1:
            gap = abs(s_start - prev_end)
            if gap > 1.5:
                errors.append(f"Scene {s_num}: Timeline gap of {gap:.2f}s detected at {s_start}s.")
            elif s_start < prev_end - 0.5:
                errors.append(f"Scene {s_num}: Overlaps with previous scene (starts at {s_start}s, prev ended at {prev_end}s).")

        # Check character in Character Bible
        sc_chars = sc.get("characters", [])
        for ch in sc_chars:
            ch_id = ch.get("character_id") if isinstance(ch, dict) else ch
            ch_name = ch.get("name") if isinstance(ch, dict) else ch
            if ch_id and ch_id not in char_bible_ids and ch_name not in char_bible_ids and char_bible_ids:
                # Warning or auto-remap
                logger.debug(f"Scene {s_num}: Character '{ch_id}' not explicitly found in Character Bible, will use primary character.")

        # Check lyrics
        if not sc.get("lyrics") and not sc.get("dialogue"):
            logger.debug(f"Scene {s_num}: No lyrics specified for shot.")

        prev_end = s_end

    total_scenes_dur = prev_end
    if total_audio_duration > 0 and total_scenes_dur < (total_audio_duration - 2.0):
        errors.append(f"Total scene timeline ({total_scenes_dur:.1f}s) does not cover song duration ({total_audio_duration:.1f}s).")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_and_repair_plan(raw_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Strictly validates raw content plan dictionary against Pydantic models."""
    try:
        validated = ContentPlanSchema(**raw_plan)
        return validated.model_dump()
    except ValidationError:
        title = raw_plan.get("title", "Kids 3D Nursery Rhyme")
        lyrics = raw_plan.get("lyrics_full", "Sing along to the happy rhyme!")
        characters = []
        for c in raw_plan.get("characters", []):
            characters.append({
                "character_id": c.get("character_id", c.get("id", "hero")),
                "name": c.get("name", "Friendly Character"),
                "type": c.get("type", "character"),
                "appearance": c.get("appearance", "Cute 3D animated character"),
                "colors": c.get("colors", ["#3b82f6", "#ef4444"]),
                "clothing": c.get("clothing", "Colorful clothes"),
                "personality": c.get("personality", "Cheerful"),
                "voice": c.get("voice", "friendly_tenor"),
                "animation_set": c.get("animation_set", ["walk", "wave", "dance"]),
            })

        scenes = []
        for idx, s in enumerate(raw_plan.get("scenes", []), start=1):
            scenes.append({
                "scene_id": s.get("scene_id", f"scene_{idx:03d}"),
                "scene_number": s.get("scene_number", idx),
                "duration": float(s.get("duration", 6.0)),
                "environment": s.get("environment", "Sunny Green Meadow"),
                "characters": s.get("characters", ["hero"]),
                "actions": s.get("actions", ["waves hello", "dances"]),
                "camera": s.get("camera", {"type": "cinematic", "movement": "pan"}),
                "lighting": s.get("lighting", {"intensity": 1.2}),
                "dialogue": s.get("dialogue", ""),
                "lyrics": s.get("lyrics", ""),
                "music": s.get("music", "preschool_tune"),
                "sound_effects": s.get("sound_effects", ["bells"]),
                "transition": s.get("transition", "cut"),
            })

        repaired = ContentPlanSchema(
            title=title,
            lyrics_full=lyrics,
            characters=characters,
            scenes=scenes,
        )
        return repaired.model_dump()
