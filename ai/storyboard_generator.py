import json
import logging
from typing import Dict, Any, List, Optional
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.storyboard")


def _compose_video_prompt(
    char_name: str,
    char_appearance: str,
    char_clothing: str,
    env_name: str,
    action: str,
    lyrics: str,
    cam: Dict[str, Any],
    scene_num: int,
) -> str:
    """Generates high-fidelity 3D preschool video generation prompts for AI engines (Luma, Kling, Seedance, Runway, Sora)."""
    clean_app = char_appearance or "cute animated toddler character with bright expressive eyes, rosy cheeks, and warm joyful smile"
    clean_cloth = char_clothing or "vibrant colorful preschool overalls and sneakers"
    clean_env = env_name or "vibrant preschool storybook meadow with blooming toy flowers and soft rainbow clouds"
    cam_move = cam.get("movement", "smooth cinematic push-in")
    cam_shot = cam.get("shot", "medium tracking shot")
    cam_angle = cam.get("angle", "eye-level")
    lighting = cam.get("lighting", "warm golden morning sunlight with gentle rim light")

    action_view = action or f"joyfully dancing and singing with playful hand gestures"

    return (
        f"Original 3D Stylized CGI Animation: {char_name}, {clean_app}, wearing {clean_cloth}. "
        f"Visual View & Action: {char_name} is {action_view}, performing in perfect synchronization to the melody line: '{lyrics}'. "
        f"Environment & Scene: {clean_env} with vibrant interactive playground props, dancing musical notes, and floating sun sparkles. "
        f"Cinematography: {cam_move} {cam_shot} from {cam_angle}, {lighting}, shallow depth of field bokeh, "
        f"Unreal Engine 5 render, raytraced subsurface scattering, vibrant saturated preschool colors, fluid toddler motion, 8k ultra-detailed."
    )


def generate_storyboard(
    topic: str,
    approved_lyrics: str,
    audio_timeline: Dict[str, Any],
    characters: List[Dict[str, Any]],
    environments: List[Dict[str, Any]],
    visual_bible: Optional[Dict[str, Any]] = None,
    target_scene_duration: float = 8.0,
) -> List[Dict[str, Any]]:
    """
    Generates structured 3D animation scene timeline based on:
    - approved lyrics
    - audio timeline (actual song duration, sections, lyric timestamps)
    - Character Bible
    - environments & visual bible
    - target_scene_duration (default: 8.0s, selectable e.g. 8s, 9s, 10s)

    Target scene duration: user-selected target (e.g. 8s, 9s, 10s).
    Every scene strictly maps to the lyrics/audio and includes a dedicated, production-ready video_prompt.
    """
    duration = float(audio_timeline.get("duration", 60.0))
    lyric_timestamps = audio_timeline.get("lyrics_timestamps", [])
    char_ids = [c.get("character_id") or c.get("id") or c.get("name") for c in characters]
    main_char = characters[0] if characters else {}
    main_char_id = char_ids[0] if char_ids else "hero_char"
    main_char_name = main_char.get("name", "Hero")
    main_char_app = main_char.get("appearance", "")
    main_char_clothing = main_char.get("clothing", "")

    main_env = environments[0] if environments else {}
    main_env_id = main_env.get("id", "env_01")
    main_env_name = main_env.get("name", "Preschool Wonderland")

    provider = get_ai_provider()

    min_dur = max(4.0, target_scene_duration - 1.5)
    max_dur = min(15.0, target_scene_duration + 2.0)

    prompt = f"""Generate a structured, synchronized 3D animation Storyboard Scene Timeline for: '{topic}'.
Total Audio Duration: {duration:.2f} seconds.
Target Per-Scene Duration: approximately {target_scene_duration:.1f} seconds (acceptable range {min_dur:.1f}s to {max_dur:.1f}s per scene).
Approved Lyrics & Timestamps:
{json.dumps(lyric_timestamps, indent=2)}

Character Bible Available:
{json.dumps(characters, indent=2)}

Environments:
{json.dumps(environments, indent=2)}

RULES:
1. Every scene duration MUST be approximately {target_scene_duration:.1f} seconds (between {min_dur:.1f}s and {max_dur:.1f}s).
2. The entire timeline (start_time 0.0 to {duration:.2f}s) MUST be fully covered without overlaps or gaps.
3. Every scene MUST map directly to the lyrics sung during that time interval.
4. Only use character IDs from the Character Bible: {char_ids}.
5. CRITICAL VIDEO GENERATION PROMPT REQUIREMENT:
   Every single scene MUST have a dedicated, rich, highly-descriptive 'video_prompt' tailored for AI Video Generators (Luma Dream Machine, Kling AI, Seedance 2.0, Runway Gen-3, Sora).
   The 'video_prompt' MUST NOT just be the lyrics line! It must vividly describe what is visually visible in the scene:
   - High-end 3D preschool character CGI animation, vibrant colors, raytraced lighting, 8k render.
   - Character specifics: name, adorable appearance, clothing, cute joyful facial expressions and toddler movements.
   - Scene Visual Action & View: What happens visually on screen during these specific lyrics.
   - Environment props, background world, floating elements.
   - Camera movement (smooth push-in, pan, orbit) and warm soft volumetric lighting.

Return a JSON object with a 'scenes' list of scene objects matching this strict schema:
{{
  "scene_id": "scene_001",
  "scene_number": 1,
  "start_time": 0.0,
  "duration": 6.0,
  "end_time": 6.0,
  "lyrics": "Exact lyrics line sung in this shot",
  "video_prompt": "Original 3D Stylized CGI Animation: [Character Name], [appearance and clothing]. Visual View & Action: [Character] is [specific cheerful toddler action], [environment and props], [camera movement and angle], [warm lighting], vibrant saturated colors, 8k ultra-detailed nursery rhyme render.",
  "characters": [
    {{
      "character_id": "{main_char_id}",
      "name": "{main_char_name}",
      "action": "bounce_and_wave"
    }}
  ],
  "environment": {{
    "id": "{main_env_id}",
    "name": "{main_env_name}"
  }},
  "actions": ["{main_char_name} dances happily", "camera tracks smoothly"],
  "camera": {{
    "shot": "wide",
    "movement": "slow_push_in",
    "angle": "eye_level"
  }},
  "emotion": "happy",
  "lighting": "bright_soft",
  "animation": ["bounce", "wave"],
  "transition": "cut"
}}"""

    system_prompt = "You are an elite 3D children animation director. Output strictly original, copyright-free scene prompts. Output a strict JSON object with a 'scenes' array covering the full audio duration. Every scene must have a rich, comprehensive video_prompt. Return valid JSON only."

    try:
        res = provider.generate_json(prompt, system_prompt)
        if res and "scenes" in res and isinstance(res["scenes"], list) and len(res["scenes"]) > 0:
            logger.info(f"Generated {len(res['scenes'])} scenes via {provider.__class__.__name__}")
            # Ensure every scene has a complete video_prompt
            for idx, s in enumerate(res["scenes"], start=1):
                p_val = s.get("video_prompt") or s.get("prompt") or s.get("visual_prompt")
                lyr_val = s.get("lyrics") or ""
                if not p_val or p_val.strip() == lyr_val.strip() or len(p_val.strip()) < 35:
                    action_txt = ", ".join(s.get("actions", [])) if isinstance(s.get("actions"), list) else "dancing cheerfully"
                    cam_dict = s.get("camera") if isinstance(s.get("camera"), dict) else {"movement": "smooth push-in", "shot": "medium", "angle": "eye_level"}
                    env_dict = s.get("environment")
                    env_name = env_dict.get("name", main_env_name) if isinstance(env_dict, dict) else str(env_dict or main_env_name)
                    s["video_prompt"] = _compose_video_prompt(
                        char_name=main_char_name,
                        char_appearance=main_char_app,
                        char_clothing=main_char_clothing,
                        env_name=env_name,
                        action=action_txt,
                        lyrics=lyr_val,
                        cam=cam_dict,
                        scene_num=idx,
                    )
                else:
                    s["video_prompt"] = p_val
            return res["scenes"]
    except Exception as e:
        logger.warning(f"AI storyboard generation failed, using procedural builder: {e}")

    # Fallback procedural storyboard engine
    return build_procedural_storyboard(
        duration,
        lyric_timestamps,
        characters,
        environments,
        target_scene_duration=target_scene_duration,
    )


def build_procedural_storyboard(
    total_duration: float,
    lyric_timestamps: List[Dict[str, Any]],
    characters: List[Dict[str, Any]],
    environments: List[Dict[str, Any]],
    target_scene_duration: float = 8.0,
) -> List[Dict[str, Any]]:
    """Procedural timeline shot generator creating user-targeted (e.g. 8s, 9s, 10s) synchronized scenes with full video_prompts."""
    char_obj = characters[0] if characters else {"character_id": "hero_01", "name": "Hero", "appearance": "cute toddler character with big round sparkling eyes", "clothing": "bright yellow overalls"}
    char_id = char_obj.get("character_id") or char_obj.get("id", "hero_01")
    char_name = char_obj.get("name", "Hero")
    char_app = char_obj.get("appearance", "cute toddler with cheerful smile and bright curious eyes")
    char_cloth = char_obj.get("clothing", "colorful preschool outfit")

    env_obj = environments[0] if environments else {"id": "env_01", "name": "Sunny Storybook World"}
    env_name = env_obj.get("name", "Sunny Storybook World")

    camera_presets = [
        {"shot": "wide", "movement": "slow_push_in", "angle": "eye_level", "lighting": "bright_sunny"},
        {"shot": "medium", "movement": "tracking_right", "angle": "low_angle", "lighting": "vibrant_daylight"},
        {"shot": "close_up", "movement": "gentle_pan", "angle": "eye_level", "lighting": "warm_rim_light"},
        {"shot": "high_angle", "movement": "crane_down", "angle": "high_three_quarter", "lighting": "golden_hour"},
    ]

    action_presets = [
        "bouncing rhythmically and waving happily with both hands",
        "dancing in circles with playful toddler giggles and joyful clapping",
        "jumping joyfully over colorful toy flowers and smiling at the viewer",
        "pointing up enthusiastically towards rainbow clouds with sparkle effects",
        "stepping side-to-side in a cute preschool choreography",
        "spinning around with wide cheerful arms and celebratory confetti sparkles",
    ]

    scenes = []
    current_time = 0.0
    scene_idx = 1

    if lyric_timestamps:
        # Group lyric lines together to match target_scene_duration (e.g. 8s, 9s, 10s)
        i = 0
        n = len(lyric_timestamps)
        while i < n:
            chunk_start = lyric_timestamps[i]["start"]
            chunk_lines = [lyric_timestamps[i].get("line", "")]
            chunk_end = lyric_timestamps[i]["end"]
            i += 1

            while i < n and (chunk_end - chunk_start) < (target_scene_duration - 1.5):
                chunk_lines.append(lyric_timestamps[i].get("line", ""))
                chunk_end = lyric_timestamps[i]["end"]
                i += 1

            s_dur = max(4.0, chunk_end - chunk_start)
            cam = camera_presets[(scene_idx - 1) % len(camera_presets)]
            action_desc = action_presets[(scene_idx - 1) % len(action_presets)]
            lyrics_line = " ".join(l for l in chunk_lines if l.strip())

            video_prompt = _compose_video_prompt(
                char_name=char_name,
                char_appearance=char_app,
                char_clothing=char_cloth,
                env_name=env_name,
                action=action_desc,
                lyrics=lyrics_line,
                cam=cam,
                scene_num=scene_idx,
            )

            scene = {
                "scene_id": f"scene_{scene_idx:03d}",
                "scene_number": scene_idx,
                "start_time": round(chunk_start, 2),
                "duration": round(s_dur, 2),
                "end_time": round(chunk_start + s_dur, 2),
                "lyrics": lyrics_line,
                "video_prompt": video_prompt,
                "characters": [
                    {
                        "character_id": char_id,
                        "name": char_name,
                        "action": "bounce_dance" if scene_idx % 2 == 0 else "wave_hello",
                    }
                ],
                "environment": env_name,
                "environment_profile": env_obj,
                "actions": [f"{char_name} {action_desc}", "camera tracks smoothly"],
                "camera": cam,
                "emotion": "joyful",
                "lighting": cam["lighting"],
                "animation": ["dance", "bounce", "wave"],
                "transition": "crossfade" if i >= n else "cut",
                "status": "PENDING",
            }
            scenes.append(scene)
            current_time = chunk_start + s_dur
            scene_idx += 1
    else:
        # Generate generic shots matching target_scene_duration (e.g. 8s, 9s, 10s)
        target_shot_dur = float(target_scene_duration or 8.0)

        while current_time < total_duration:
            dur = min(target_shot_dur, total_duration - current_time)
            if dur < 2.0:
                if scenes:
                    scenes[-1]["duration"] += dur
                    scenes[-1]["end_time"] = total_duration
                break

            cam = camera_presets[(scene_idx - 1) % len(camera_presets)]
            action_desc = action_presets[(scene_idx - 1) % len(action_presets)]
            lyrics_line = f"Singing our cheerful preschool nursery song (Scene {scene_idx})"

            video_prompt = _compose_video_prompt(
                char_name=char_name,
                char_appearance=char_app,
                char_clothing=char_cloth,
                env_name=env_name,
                action=action_desc,
                lyrics=lyrics_line,
                cam=cam,
                scene_num=scene_idx,
            )

            scene = {
                "scene_id": f"scene_{scene_idx:03d}",
                "scene_number": scene_idx,
                "start_time": round(current_time, 2),
                "duration": round(dur, 2),
                "end_time": round(current_time + dur, 2),
                "lyrics": lyrics_line,
                "video_prompt": video_prompt,
                "characters": [
                    {
                        "character_id": char_id,
                        "name": char_name,
                        "action": "bounce",
                    }
                ],
                "environment": env_name,
                "environment_profile": env_obj,
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
