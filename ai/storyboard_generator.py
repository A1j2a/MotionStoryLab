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
    topic: str = "",
    char_species: str = "",
    char_colors: str = "",
    additional_chars: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Generates high-fidelity 3D preschool video generation prompts matching Pixar/CoComelon benchmark.
    Character appearance, clothing and topic are strictly enforced so AI generators always
    render the correct character with the right costume themed around the song topic."""
    clean_app = char_appearance or "cute animated toddler character with large round expressive eyes, rosy cheeks, and joyful warm smile"
    clean_cloth = char_clothing or "vibrant preschool dungarees, colorful t-shirt, and sneakers"
    clean_env = env_name or "vibrant sunlit storybook farm with rustic wooden barn, blooming flowers, and lush green meadows"
    cam_move = cam.get("movement", "smooth cinematic push-in")
    cam_shot = cam.get("shot", "medium tracking shot")
    cam_angle = cam.get("angle", "eye-level")
    lighting = cam.get("lighting", "warm golden morning sunlight with gentle rim light")

    action_view = action or "joyfully dancing, bouncing rhythmically, and gesturing enthusiastically"

    extra_chars_str = ""
    if additional_chars:
        extra_names = ", ".join([c.get("name", "friend") for c in additional_chars[:2]])
        extra_chars_str = f" alongside {extra_names} joining the cheerful choreography,"

    # Build a rich character identity block so the AI generator knows exactly what the character looks like
    char_identity_parts = [f"{char_name}"]
    if char_species:
        char_identity_parts.append(f"({char_species})")
    char_identity_parts.append(f"— {clean_app}")
    if clean_cloth:
        char_identity_parts.append(f"wearing {clean_cloth}")
    if char_colors:
        char_identity_parts.append(f"in palette {char_colors}")
    char_identity = ", ".join(char_identity_parts)

    topic_tag = f" themed around '{topic}'" if topic else ""

    return (
        f"Original 3D Stylized Pixar and CoComelon CGI Animation: {char_identity}{extra_chars_str}. "
        f"Song Topic{topic_tag}. "
        f"Visual Action & Narrative: {char_name} is {action_view}, directly acting out and visually narrating the lyrics: '{lyrics}'. "
        f"Environment & Scene: {clean_env} under bright blue sunny skies with warm volumetric sunbeams and vibrant saturated preschool palette. "
        f"Cinematography: {cam_move} {cam_shot} from {cam_angle}, {lighting}, shallow depth of field bokeh, "
        f"8K Unreal Engine 5 render, raytraced subsurface scattering on skin, glossy expressive cartoon eyes, fluid toddler motion."
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
    Generates structured 3D animation scene timeline.

    FLOW (deterministic-first):
    1. ALWAYS build scenes procedurally from song duration + lyric timestamps.
       This guarantees: correct scene count = ceil(song_duration / target_scene_duration),
       correct per-scene duration = target_scene_duration, lyrics-synced.
    2. Optionally enrich video_prompts via AI (does NOT change scene count or durations).
    """
    duration = float(audio_timeline.get("duration", 60.0))
    lyric_timestamps = audio_timeline.get("lyrics_timestamps", [])

    main_char = characters[0] if characters else {}
    main_char_id = main_char.get("character_id") or main_char.get("id") or main_char.get("name", "hero_01")
    main_char_name = main_char.get("name", "Hero")
    main_char_app = main_char.get("appearance", "")
    main_char_clothing = main_char.get("clothing", "")
    main_env = environments[0] if environments else {}
    main_env_name = main_env.get("name", "Preschool Wonderland")

    # ── STEP 1: Build scenes procedurally (always correct count + duration) ──
    scenes = build_procedural_storyboard(
        total_duration=duration,
        lyric_timestamps=lyric_timestamps,
        characters=characters,
        environments=environments,
        target_scene_duration=target_scene_duration,
        topic=topic,
    )

    logger.info(
        f"Procedural storyboard: {len(scenes)} scenes @ {target_scene_duration}s target "
        f"for {duration:.1f}s song"
    )

    # ── STEP 2: Enrich video_prompts via AI (best-effort, never changes count/duration) ──
    provider = get_ai_provider()
    lyric_lines_for_ai = [
        {"scene_number": s["scene_number"], "lyrics": s.get("lyrics", "")}
        for s in scenes
    ]

    all_chars_desc = ", ".join([
        f"{c.get('name', 'Character')} "
        f"({c.get('species', c.get('type', 'character'))}) — "
        f"{c.get('appearance', 'cute toddler')}, wearing {c.get('clothing', 'preschool outfit')}"
        + (f", colors: {', '.join(c['colors']) if isinstance(c.get('colors'), list) else c.get('colors', '')}" if c.get('colors') else "")
        for c in characters[:3]
    ]) if characters else f"{main_char_name} — {main_char_app}, wearing {main_char_clothing}"

    enrich_prompt = f"""You are an elite 3D children animation director specializing in top-tier Pixar and CoComelon CGI preschool animations.
Topic: '{topic}'
Cast & Characters: {all_chars_desc}
Environment / Setting: {main_env_name}

I have {len(scenes)} scenes already planned at {target_scene_duration}s each.
For EACH scene below, write ONE rich, production-ready 'video_prompt' for AI Video Generators (Google Flow, Luma, Kling, Wan 2.1, Runway, Sora).

CRITICAL CHARACTER RULES:
- The character(s) MUST appear exactly as described: their appearance, clothing, colors, and species are NON-NEGOTIABLE.
- Never change the character's costume, colors, or identity between scenes.
- The song topic is '{topic}' — every scene prompt MUST visually connect to this topic.

VISUAL BENCHMARK (Strictly Follow Reference Quality):
- Style: Stylized 3D Pixar & CoComelon CGI Animation, vibrant saturated preschool candy palette, 8K Unreal Engine 5 render.
- Character Aesthetics: Smooth porcelain skin with soft subsurface scattering, large round expressive glossy cartoon eyes, rosy cheeks, warm joyful facial expressions.
- Acting & Lyrics Alignment: The visual choreography MUST strictly act out the specific lyric line for that scene. Characters must physically perform the actions, gestures, and story mentioned in the lyrics.
- Camera & Lighting: Cinematic camera motion (tracking, slow push-in, gentle crane), soft 3-point studio lighting with warm golden sunbeams and shallow depth of field bokeh.
- Length: 2 to 4 rich descriptive sentences per prompt.

Scenes to enrich:
{json.dumps(lyric_lines_for_ai, indent=2)}

Return a JSON object: {{"prompts": [{{"scene_number": 1, "video_prompt": "..."}}]}}
IMPORTANT: Return EXACTLY {len(scenes)} prompts, one per scene. Do NOT add or remove scenes."""
    try:
        res = provider.generate_json(
            enrich_prompt,
            "You are an elite 3D Pixar/CoComelon animation director. Return valid JSON only."
        )
        if res and "prompts" in res and isinstance(res["prompts"], list):
            prompt_map = {
                p["scene_number"]: p.get("video_prompt", "")
                for p in res["prompts"]
                if isinstance(p, dict) and p.get("video_prompt")
            }
            for s in scenes:
                ai_prompt = prompt_map.get(s["scene_number"], "")
                if ai_prompt and len(ai_prompt.strip()) > 40:
                    s["video_prompt"] = ai_prompt.strip()
            logger.info(f"AI enriched {len(prompt_map)}/{len(scenes)} scene prompts")
    except Exception as e:
        logger.warning(f"AI prompt enrichment failed (using procedural prompts): {e}")

    return scenes


def build_procedural_storyboard(
    total_duration: float,
    lyric_timestamps: List[Dict[str, Any]],
    characters: List[Dict[str, Any]],
    environments: List[Dict[str, Any]],
    target_scene_duration: float = 8.0,
    topic: str = "",
) -> List[Dict[str, Any]]:
    """
    Builds a deterministic scene timeline where:
    - Every scene is EXACTLY target_scene_duration seconds
    - Scene count = ceil(total_duration / target_scene_duration)
    - Lyrics are assigned to each scene by time overlap (not grouped by lyric lines)
    - Last scene gets remaining duration (may be shorter)

    This guarantees: 8s selected → all scenes 8.0s, 120s song → 15 scenes.
    """
    char_obj = characters[0] if characters else {
        "character_id": "hero_01", "name": "Hero",
        "appearance": "cute toddler character with big round sparkling eyes",
        "clothing": "bright yellow overalls",
    }
    char_id = char_obj.get("character_id") or char_obj.get("id", "hero_01")
    char_name = char_obj.get("name", "Hero")
    char_app = char_obj.get("appearance", "cute toddler with cheerful smile and bright curious eyes")
    char_cloth = char_obj.get("clothing", "colorful preschool outfit")
    char_species = char_obj.get("species") or char_obj.get("type", "")
    raw_colors = char_obj.get("colors", [])
    char_colors = ", ".join(raw_colors) if isinstance(raw_colors, list) else str(raw_colors or "")
    extra_chars = characters[1:] if len(characters) > 1 else None

    env_obj = environments[0] if environments else {"id": "env_01", "name": "Sunny Storybook World"}
    env_name = env_obj.get("name", "Sunny Storybook World")

    camera_presets = [
        {"shot": "wide",       "movement": "slow_push_in",    "angle": "eye_level",          "lighting": "bright_sunny"},
        {"shot": "medium",     "movement": "tracking_right",   "angle": "low_angle",           "lighting": "vibrant_daylight"},
        {"shot": "close_up",   "movement": "gentle_pan",       "angle": "eye_level",           "lighting": "warm_rim_light"},
        {"shot": "high_angle", "movement": "crane_down",       "angle": "high_three_quarter",  "lighting": "golden_hour"},
    ]
    action_presets = [
        "bouncing rhythmically and waving happily with both hands",
        "dancing in circles with playful toddler giggles and joyful clapping",
        "jumping joyfully over colorful toy flowers and smiling at the viewer",
        "pointing up enthusiastically towards rainbow clouds with sparkle effects",
        "stepping side-to-side in a cute preschool choreography",
        "spinning around with wide cheerful arms and celebratory confetti sparkles",
    ]

    import math
    target = float(target_scene_duration)
    total = float(total_duration)

    # ── Calculate exact scene count from song duration ──
    num_scenes = max(1, math.ceil(total / target))

    scenes = []
    for idx in range(1, num_scenes + 1):
        scene_start = (idx - 1) * target
        scene_end = min(idx * target, total)
        scene_dur = round(scene_end - scene_start, 2)

        # ── Assign lyrics: collect all lines whose window overlaps this scene ──
        overlapping_lines: List[str] = []
        if lyric_timestamps:
            for lt in lyric_timestamps:
                lt_start = float(lt.get("start", 0))
                lt_end = float(lt.get("end", 0))
                # Overlap: lyric starts before scene ends AND lyric ends after scene starts
                if lt_start < scene_end and lt_end > scene_start:
                    line = lt.get("line", "").strip()
                    if line:
                        overlapping_lines.append(line)
        lyrics_line = " ".join(overlapping_lines) if overlapping_lines else ""

        cam = camera_presets[(idx - 1) % len(camera_presets)]
        action_desc = action_presets[(idx - 1) % len(action_presets)]

        video_prompt = _compose_video_prompt(
            char_name=char_name,
            char_appearance=char_app,
            char_clothing=char_cloth,
            env_name=env_name,
            action=action_desc,
            lyrics=lyrics_line,
            cam=cam,
            scene_num=idx,
            topic=topic,
            char_species=char_species,
            char_colors=char_colors,
            additional_chars=extra_chars,
        )

        scene = {
            "scene_id": f"scene_{idx:03d}",
            "scene_number": idx,
            "start_time": round(scene_start, 2),
            "duration": scene_dur,
            "end_time": round(scene_end, 2),
            "lyrics": lyrics_line,
            "video_prompt": video_prompt,
            "characters": [
                {
                    "character_id": char_id,
                    "name": char_name,
                    "action": "bounce_dance" if idx % 2 == 0 else "wave_hello",
                }
            ],
            "environment": env_name,
            "environment_profile": env_obj,
            "actions": [f"{char_name} {action_desc}", "camera tracks smoothly"],
            "camera": cam,
            "emotion": "joyful",
            "lighting": cam["lighting"],
            "animation": ["dance", "bounce", "wave"],
            "transition": "crossfade" if idx == num_scenes else "cut",
            "status": "PENDING",
        }
        scenes.append(scene)

    return scenes


