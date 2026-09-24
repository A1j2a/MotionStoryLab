import json
import logging
from typing import Dict, Any, List, Optional
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.storyboard")


def generate_storyboard(
    topic: str,
    approved_lyrics: str,
    audio_timeline: Dict[str, Any],
    characters: List[Dict[str, Any]],
    environments: List[Dict[str, Any]],
    visual_bible: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Generates structured 3D animation scene timeline based on:
    - approved lyrics
    - audio timeline (actual song duration, sections, lyric timestamps)
    - Character Bible
    - environments & visual bible

    Target scene duration: 5–10 seconds normally (dynamic).
    Every scene strictly maps to the lyrics/audio.
    """
    duration = float(audio_timeline.get("duration", 60.0))
    lyric_timestamps = audio_timeline.get("lyrics_timestamps", [])
    char_ids = [c.get("character_id") or c.get("id") or c.get("name") for c in characters]
    main_char_id = char_ids[0] if char_ids else "hero_char"
    main_char_name = characters[0].get("name", "Hero") if characters else "Hero"
    main_env_id = environments[0].get("id", "env_01") if environments else "env_01"

    provider = get_ai_provider()

    prompt = f"""Generate a structured, synchronized 3D animation Storyboard Scene Timeline for: '{topic}'.
Total Audio Duration: {duration:.2f} seconds.
Approved Lyrics & Timestamps:
{json.dumps(lyric_timestamps, indent=2)}

Character Bible Available:
{json.dumps(characters, indent=2)}

Environments:
{json.dumps(environments, indent=2)}

RULES:
1. Every scene duration MUST be between 5.0 and 10.0 seconds (except possibly short intro/outro).
2. The entire timeline (start_time 0.0 to {duration:.2f}s) MUST be fully covered without overlaps or gaps.
3. Every scene MUST map directly to the lyrics sung during that time interval.
4. Only use character IDs from the Character Bible: {char_ids}.
5. Return a JSON object with a "scenes" list of scene objects matching this strict schema:
{{
  "scene_id": "scene_001",
  "scene_number": 1,
  "start_time": 0.0,
  "duration": 6.0,
  "end_time": 6.0,
  "lyrics": "Exact lyrics line",
  "characters": [
    {{
      "character_id": "{main_char_id}",
      "name": "{main_char_name}",
      "action": "wave"
    }}
  ],
  "environment": {{
    "id": "{main_env_id}",
    "name": "Main Environment"
  }},
  "actions": ["character waves", "camera tracks smoothly"],
  "camera": {{
    "shot": "wide",
    "movement": "slow_push_in",
    "angle": "eye_level"
  }},
  "emotion": "happy",
  "lighting": "bright_soft",
  "animation": ["wave", "bounce"],
  "transition": "cut"
}}"""

    system_prompt = "You are a professional 3D animation director (Cocomelon, Pixar). Output a strict JSON array of scenes covering the full audio duration. Return valid JSON only."

    try:
        res = provider.generate_json(prompt, system_prompt)
        if res and "scenes" in res and isinstance(res["scenes"], list) and len(res["scenes"]) > 0:
            logger.info(f"Generated {len(res['scenes'])} scenes via {provider.__class__.__name__}")
            return res["scenes"]
    except Exception as e:
        logger.warning(f"AI storyboard generation failed, using procedural builder: {e}")

    # Fallback procedural storyboard engine
    return build_procedural_storyboard(duration, lyric_timestamps, characters, environments)


def build_procedural_storyboard(
    total_duration: float,
    lyric_timestamps: List[Dict[str, Any]],
    characters: List[Dict[str, Any]],
    environments: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Procedural timeline shot generator creating 5-8s synchronized scenes."""
    char_obj = characters[0] if characters else {"character_id": "hero_01", "name": "Hero"}
    char_id = char_obj.get("character_id") or char_obj.get("id", "hero_01")
    char_name = char_obj.get("name", "Hero")
    env_obj = environments[0] if environments else {"id": "env_01", "name": "Sunny World"}

    camera_presets = [
        {"shot": "wide", "movement": "slow_push_in", "angle": "eye_level", "lighting": "bright_sunny"},
        {"shot": "medium", "movement": "tracking_right", "angle": "low_angle", "lighting": "vibrant_daylight"},
        {"shot": "close_up", "movement": "gentle_pan", "angle": "eye_level", "lighting": "warm_rim_light"},
        {"shot": "high_angle", "movement": "crane_down", "angle": "high_three_quarter", "lighting": "golden_hour"},
    ]

    scenes = []
    current_time = 0.0
    scene_idx = 1

    if lyric_timestamps:
        # Group lyric timestamps into 5–8 second chunks
        for idx, ts in enumerate(lyric_timestamps, start=1):
            s_start = ts["start"]
            s_end = ts["end"]
            s_dur = max(4.0, s_end - s_start)
            cam = camera_presets[(scene_idx - 1) % len(camera_presets)]

            scene = {
                "scene_id": f"scene_{scene_idx:03d}",
                "scene_number": scene_idx,
                "start_time": round(s_start, 2),
                "duration": round(s_dur, 2),
                "end_time": round(s_start + s_dur, 2),
                "lyrics": ts.get("line", ""),
                "characters": [
                    {
                        "character_id": char_id,
                        "name": char_name,
                        "action": "bounce_dance" if idx % 2 == 0 else "wave_hello",
                    }
                ],
                "environment": env_obj,
                "actions": [f"{char_name} performs joyfully", "camera follows movement"],
                "camera": cam,
                "emotion": "joyful" if idx < len(lyric_timestamps) else "gentle_happy",
                "lighting": cam["lighting"],
                "animation": ["dance", "bounce", "wave"],
                "transition": "crossfade" if idx == len(lyric_timestamps) else "cut",
                "status": "PENDING",
            }
            scenes.append(scene)
            current_time = s_start + s_dur
            scene_idx += 1
    else:
        # Generate generic 6-second shots covering total duration
        target_shot_dur = 6.0
        while current_time < total_duration:
            dur = min(target_shot_dur, total_duration - current_time)
            if dur < 2.0:
                if scenes:
                    scenes[-1]["duration"] += dur
                    scenes[-1]["end_time"] = total_duration
                break

            cam = camera_presets[(scene_idx - 1) % len(camera_presets)]
            scene = {
                "scene_id": f"scene_{scene_idx:03d}",
                "scene_number": scene_idx,
                "start_time": round(current_time, 2),
                "duration": round(dur, 2),
                "end_time": round(current_time + dur, 2),
                "lyrics": f"Singing our cheerful preschool nursery song (Scene {scene_idx})",
                "characters": [
                    {
                        "character_id": char_id,
                        "name": char_name,
                        "action": "bounce",
                    }
                ],
                "environment": env_obj,
                "actions": [f"{char_name} sings along with melody"],
                "camera": cam,
                "emotion": "happy",
                "lighting": cam["lighting"],
                "animation": ["bounce", "smile"],
                "transition": "cut",
                "status": "PENDING",
            }
            scenes.append(scene)
            current_time += dur
            scene_idx += 1

    return scenes
