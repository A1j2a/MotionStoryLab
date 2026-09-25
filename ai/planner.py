import os
import re
import json
import logging
import urllib.request
from typing import Dict, Any, List, Optional

logger = logging.getLogger("studio.planner")


def call_claude_if_available(prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
    """
    Calls Anthropic Claude 3.5 API directly for state-of-the-art YouTube SEO and lyrics planning.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", os.environ.get("CLAUDE_API_KEY", "")).strip()
    if not api_key:
        return None

    model = os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022").strip()
    target_url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": model,
        "max_tokens": 2048,
        "system": system_prompt or "You are an elite preschool animation and YouTube Kids SEO master (100% original, copyright-free). Return valid JSON only.",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    try:
        req = urllib.request.Request(
            target_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                resp_data = json.loads(response.read().decode("utf-8"))
                for block in resp_data.get("content", []):
                    if block.get("type") == "text":
                        raw_text = block.get("text", "")
                        clean_json = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
                        clean_json = re.sub(r"```$", "", clean_json.strip(), flags=re.MULTILINE)
                        return json.loads(clean_json)
    except Exception as e:
        logger.warning(f"Claude API call bypassed: {e}")
        return None


def call_llm_if_available(prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
    """
    Calls Anthropic Claude first, then native Ollama endpoint (http://127.0.0.1:11434/v1/chat/completions)
    or OpenAI endpoints. Returns parsed JSON or None if offline.
    """
    # 1. Try Claude if configured
    claude_res = call_claude_if_available(prompt, system_prompt)
    if claude_res:
        return claude_res

    # 2. Try Ollama (Local Metal M4)
    ollama_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").strip()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip()

    if base_url:
        target_url = f"{base_url.rstrip('/')}/chat/completions"
    elif ollama_url:
        target_url = f"{ollama_url.rstrip('/')}/v1/chat/completions"
    else:
        target_url = "http://127.0.0.1:11434/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    model = os.environ.get("OLLAMA_MODEL", os.environ.get("AI_MODEL", "llama3.2"))

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt or "You are an award-winning preschool animation creator (100% original, copyright-free). Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1800,
    }

    try:
        req = urllib.request.Request(
            target_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                resp_data = json.loads(response.read().decode("utf-8"))
                content = resp_data["choices"][0]["message"]["content"]
                clean_json = re.sub(r"^```(?:json)?\s*", "", content.strip(), flags=re.MULTILINE)
                clean_json = re.sub(r"```$", "", clean_json.strip(), flags=re.MULTILINE)
                return json.loads(clean_json)
    except Exception as e:
        logger.warning(f"External AI Gateway call to {target_url} bypassed: {e}")
        return None


def generate_preschool_lyrics(topic: str, duration_min: int = 5) -> Dict[str, Any]:
    """
    Generates original preschool nursery rhyme lyrics based strictly on user topic.
    First tries external LLM. Falls back to dynamic topic builder.
    """
    topic_clean = topic.strip().capitalize()

    # 1. Try external AI if connected
    ai_result = call_llm_if_available(
        prompt=f"Generate original preschool nursery rhyme lyrics for toddlers about: '{topic_clean}'. Provide 4 verses (Verse 1, Chorus, Verse 2, Outro) with character actions. Format as JSON with keys: title, verses (list of objects with section, lines, character, action).",
        system_prompt="You are a professional children's TV songwriter (100% original, copyright-free). Output valid JSON only."
    )
    if ai_result and "verses" in ai_result and isinstance(ai_result["verses"], list):
        return {
            "title": ai_result.get("title", topic_clean),
            "lyrics_full": "\n\n".join(
                f"[{v.get('section', 'Verse')}]\n" + "\n".join(v.get("lines", []))
                for v in ai_result["verses"]
            ),
            "verses": ai_result["verses"],
        }

    # 2. Dynamic topic-matched generator
    pkg = build_fallback_content_package(topic_clean, duration_minutes=duration_min)
    return {
        "title": pkg["title"],
        "lyrics_full": pkg["lyrics_full"],
        "verses": pkg["verses"],
    }


def generate_character_bible(topic: str) -> List[Dict[str, Any]]:
    """
    Generates consistent 3D Character Bible strictly matching the user's topic theme and characters.
    """
    topic_clean = topic.strip().capitalize()
    pkg = build_fallback_content_package(topic_clean)
    return pkg.get("characters", [])


def generate_scene_list(topic: str, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates structured 3D animation scene shots with distinct camera angles.
    """
    scenes = []
    camera_styles = [
        {"movement": "wide_establishing_pan", "fov": 45, "description": "Wide establishing pan introducing the world and character"},
        {"movement": "low_angle_tracking_action", "fov": 40, "description": "Low dynamic tracking shot showing energetic character movement"},
        {"movement": "high_three_quarter_hero", "fov": 48, "description": "Elevated panoramic beauty shot showcasing environment details"},
        {"movement": "close_up_face_farewell", "fov": 36, "description": "Warm close-up portrait of character smiling and waving goodbye"},
    ]

    for idx, v in enumerate(verses, start=1):
        cam = camera_styles[(idx - 1) % len(camera_styles)]
        scene = {
            "scene_number": idx,
            "duration": 5.0,
            "environment": f"Preschool 3D Environment {idx}",
            "characters": [v.get("character", "Hero Character")],
            "actions": [v.get("action", "dance"), "moves to musical beat"],
            "camera": {
                "type": "cinematic_preschool",
                "movement": cam["movement"],
                "fov": cam["fov"],
                "target": v.get("character", "Hero Character"),
            },
            "lighting": {
                "time_of_day": "golden_hour" if idx == len(verses) else "bright_sunny_day",
                "intensity": 1.2,
            },
            "dialogue": f"{v.get('character', 'Character')} is having fun!",
            "lyrics": " / ".join(v.get("lines", [])[:2]),
            "music": "preschool_upbeat_melody_4_4",
            "sound_effects": ["cheerful_chime", "sparkle_bells"],
            "transition": "crossfade" if idx == len(verses) else "cut",
            "status": "PENDING",
        }
        scenes.append(scene)

    return scenes


def generate_seo_metadata(
    topic: str,
    project_title: str,
    verses: Optional[List[Dict[str, Any]]] = None,
    scenes: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Generates optimized YouTube metadata package (High-CTR Title, Description, Tags, Chapters).
    """
    clean_topic = topic.strip().capitalize()

    # Try Ollama / LLM for top-ranking YouTube preschool SEO
    ai_seo = call_llm_if_available(
        prompt=f"Generate a top-ranking, high-CTR YouTube Kids metadata package for a preschool video on topic '{clean_topic}'. Return JSON with keys: title_variants (3 catchy titles with emojis), description (engaging description with lyrics and chapters), hashtags (6 trending tags), and tags (15 high-volume search keywords for YouTube Studio).",
        system_prompt="You are an expert YouTube Kids SEO strategist specializing in high CTR, COPPA compliance, and preschool search volume."
    )
    if ai_seo and isinstance(ai_seo.get("title_variants"), list) and isinstance(ai_seo.get("tags"), list):
        titles = ai_seo["title_variants"]
        return {
            "title_variants": titles,
            "selected_title": titles[0],
            "description": ai_seo.get("description", ""),
            "hashtags": ai_seo.get("hashtags", [f"#{clean_topic.replace(' ', '').lower()}", "#nurseryrhymes", "#kidssongs"]),
            "tags": ai_seo["tags"],
            "chapters": [
                {"time": "00:00", "title": "Welcome & Intro"},
                {"time": "00:15", "title": "Verse 1: Sing Along"},
                {"time": "00:30", "title": "Happy Dance Chorus"},
                {"time": "00:45", "title": "Outro & Sweet Dreams"},
            ],
        }

    titles = [
        f"{clean_topic} 🎵 Nursery Rhymes & Kids Songs | Preschool Learning",
        f"The {clean_topic} Song! ✨ Fun 3D Toddler Cartoons & Rhymes",
        f"Sing Along: {clean_topic} 🎈 Super Simple Songs for Children",
    ]

    description_body = f"""Welcome to our magical world of music and fun! Today we are singing about {clean_topic}! 🌟
Sing, dance, and learn with cute 3D cartoon characters in Pixar-grade animation.

🔔 Subscribe for weekly educational rhymes, preschool phonics, and dance-along toddler cartoons!

🎵 LYRICS:
"""
    if verses:
        for v in verses:
            description_body += f"\n[{v.get('section', 'Verse')}]\n"
            for line in v.get("lines", []):
                description_body += f"{line}\n"

    description_body += """
⏱️ VIDEO CHAPTERS:
00:00 - Welcome & Introduction
00:15 - Singing & Dancing Verse
00:30 - Happy Chorus & Beat
00:45 - Wave Goodbye & Outro

#nurseryrhymes #kidssongs #toddlerlearning #preschoolcartoons #3danimation #preschoolsongs #learningvideos
"""

    tags = [
        clean_topic.lower(),
        f"{clean_topic.lower()} song",
        f"{clean_topic.lower()} nursery rhyme",
        "nursery rhymes",
        "kids songs",
        "preschool songs",
        "toddler music",
        "baby cartoon",
        "3d animation kids",
        "sing along for toddlers",
        "kids video studio",
    ]

    return {
        "title_variants": titles,
        "selected_title": titles[0],
        "description": description_body.strip(),
        "hashtags": [
            "#nurseryrhymes",
            "#kidssongs",
            "#toddlercartoons",
            f"#{clean_topic.replace(' ', '').lower()}",
            "#preschoollearning",
            "#kidsanimation",
        ],
        "tags": tags,
        "chapters": [
            {"time": "00:00", "title": "Welcome & Intro"},
            {"time": "00:15", "title": "Verse 1: Singing & Dance"},
            {"time": "00:30", "title": "Happy Chorus Together"},
            {"time": "00:45", "title": "Outro & Sweet Dreams"},
        ],
    }
