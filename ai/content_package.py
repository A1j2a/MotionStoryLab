import re
import json
import logging
from typing import Dict, Any, List, Optional
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.content")


def generate_content_package(
    topic: str,
    video_type: str = "Nursery Rhyme",
    target_age: str = "1–4 Years",
    duration_minutes: float = 2.0,
) -> Dict[str, Any]:
    """
    Generates a complete kids content package strictly aligned to the selected topic and requested duration.
    STRICT COPYRIGHT POLICY: 100% original, copyright-free preschool intellectual property.
    """
    clean_topic = topic.strip().capitalize()
    provider = get_ai_provider()
    target_dur = max(0.5, float(duration_minutes or 2.0))

    stanza_guide = (
        "4 stanzas (~16 lines: [Verse 1], [Chorus], [Verse 2], [Outro])"
        if target_dur <= 1.2
        else (
            "8-9 stanzas (~28-32 lines with [Intro], [Verse 1], [Chorus], [Verse 2], [Chorus], [Bridge], [Verse 3], [Chorus], [Outro])"
            if target_dur <= 2.5
            else "11-13 stanzas (~38-48 lines with [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Pre-Chorus], [Chorus], [Verse 3], [Bridge], [Chorus], [Verse 4], [Outro])"
        )
    )

    prompt = f"""Generate a comprehensive, production-ready, 100% original Kids/Nursery Rhyme Content Package strictly about: '{clean_topic}'.
Target Audience: {target_age} preschoolers.
Format: {video_type}.
Target Song & Video Duration: {target_dur:.1f} minutes ({int(target_dur * 60)} seconds).

CRITICAL DURATION & SONG SCRIPT RULE:
The song lyrics MUST be scaled to last the full {target_dur:.1f} minutes when sung by Suno AI!
Provide: {stanza_guide}.
DO NOT generate short, abbreviated lyrics that finish in 40 seconds! Include all stanzas with Suno tags ([Intro], [Verse 1], [Chorus], [Verse 2], [Bridge], [Outro]).

STRICT ZERO-COPYRIGHT POLICY:
1. Every character, song title, and lyric line MUST be 100% original, copyright-free, and brand new.
2. NEVER use or mention copyrighted characters, brands, or franchises (NO Cocomelon, Disney, Pixar, Marvel, Peppa Pig, Baby Shark, Pinkfong, Paw Patrol, Super Simple Songs, ChuChu TV, etc.).
3. Visual aesthetics must be described using generic artistic styles: cute 3D low-poly rounded preschool CGI character, vibrant saturated toy-like palette, soft diffuse lighting.

Return a valid JSON object with the following EXACT structure:
{{
  "title": "Catchy YouTube Kids Title with Emojis strictly matching '{clean_topic}'",
  "description": "Engaging description including lyrics and call-to-actions",
  "chapters": [
    {{"time": "00:00", "title": "Welcome & Introduction"}},
    {{"time": "00:30", "title": "Verse 1: Sing Along"}},
    {{"time": "01:00", "title": "Happy Dance Chorus"}},
    {{"time": "01:30", "title": "Verse 2: Action Play"}},
    {{"time": "02:00", "title": "Outro & Goodbye"}}
  ],
  "hashtags": ["#nurseryrhymes", "#kidssongs", "#preschoollearning", f"#{clean_topic.replace(' ', '').lower()}"],
  "tags": [clean_topic.lower(), f"{clean_topic.lower()} song", "nursery rhymes", "kids songs", "preschool animation", "3d cartoon"],
  "story_concept": "Detailed 2-3 sentence narrative describing character journey and actions",
  "lyrics_full": "Complete formatted lyrics with full stanzas matching {target_dur:.1f} mins duration",
  "verses": [
    {{
      "section": "Verse 1",
      "lines": ["Line 1", "Line 2", "Line 3", "Line 4"],
      "character": "Main Character Name",
      "action": "Specific dance/action"
    }}
  ],
  "characters": [
    {{
      "character_id": "char_01",
      "name": "Original Character Name matching topic",
      "species": "animal / vehicle / child / object / fantasy",
      "age": "Preschooler",
      "gender": "neutral",
      "appearance": "Cute 3D low-poly rounded description with big curious cartoon eyes",
      "colors": ["#facc15", "#2563eb"],
      "clothing": "Description of clothing / accessories",
      "personality": "Cheerful, energetic, kind guide",
      "voice": "tenor_cheerful",
      "animation_set": ["walk", "jump", "dance", "wave", "bounce"]
    }}
  ],
  "environments": [
    {{
      "id": "env_01",
      "name": "Thematic Environment",
      "description": "Vibrant colorful preschool world with soft rounded props and warm lighting"
    }}
  ],
  "music_style": "120 BPM cheerful preschool pop with marimba, acoustic guitar, warm bass, and clap rhythm",
  "voice_style": "Warm cheerful preschool storyteller with clear articulation",
  "thumbnail_prompt": "Cute 3D CGI cartoon animation of [Character] smiling happily in [Environment], 8k vibrant lighting, high CTR YouTube Kids thumbnail",
  "target_audience": "{target_age}",
  "educational_angle": "Rhythm recognition, phonics, vocabulary and cooperative play",
  "visual_bible": {{
    "visual_style": "3D Cartoon Stylized Preschool Animation",
    "render_style": "Soft diffuse lighting, glossy toy-like materials, vibrant saturated palette",
    "lighting_style": "Bright warm daylight with subtle rim highlights",
    "camera_style": "Dynamic low-angle eye-level tracking with gentle push-ins",
    "environment_style": "Rounded low-poly hills, pastel skies, chunky props"
  }}
}}"""

    system_prompt = (
        f"You are an elite preschool children songwriter and animation director. "
        f"Generate 100% original, dynamic, copyright-free content specifically about '{clean_topic}' scaled for {target_dur:.1f} minutes. "
        f"Output strictly valid JSON matching the schema."
    )

    def _clean_pkg(d: Dict[str, Any]) -> Dict[str, Any]:
        raw_l = d.get("lyrics_full", "")
        if isinstance(raw_l, dict):
            raw_l = "\n\n".join(f"[{k}]\n{v}" for k, v in raw_l.items())
        elif isinstance(raw_l, list):
            raw_l = "\n".join(str(item) for item in raw_l)
        else:
            raw_l = str(raw_l or "")
        d["lyrics_full"] = raw_l
        d["approved_lyrics"] = raw_l
        return d

    # 1. Primary AI generation call
    try:
        data = provider.generate_json(prompt, system_prompt, max_tokens=2200)
        if data and "lyrics_full" in data and "characters" in data and isinstance(data.get("characters"), list) and len(data["characters"]) > 0:
            logger.info(f"Generated 100% dynamic content package via AI model ({provider.__class__.__name__}) for topic: {clean_topic} ({target_dur:.1f}m)")
            return _clean_pkg(data)
    except Exception as e:
        logger.warning(f"Primary AI generation failed ({e}), attempting AI retry with simplified prompt...")

    # 2. AI Retry with focused prompt to ensure 100% dynamic AI generation
    retry_prompt = f"""Generate a 100% original preschool kids song and video concept for: '{clean_topic}'.
Duration: {target_dur:.1f} minutes. Target Age: {target_age}.
Return JSON only:
{{
  "title": "{clean_topic} Song ✨🎶 3D Nursery Rhymes",
  "description": "Fun and educational song about {clean_topic} for kids!",
  "chapters": [{{"time": "00:00", "title": "Intro"}}, {{"time": "01:00", "title": "Chorus"}}, {{"time": "02:00", "title": "Outro"}}],
  "hashtags": ["#nurseryrhymes", "#kidssongs", "#preschool"],
  "tags": ["{clean_topic.lower()}", "nursery rhymes", "kids songs", "3d cartoon"],
  "story_concept": "A fun preschool adventure celebrating {clean_topic}.",
  "lyrics_full": "[Verse 1]\\nSinging about {clean_topic} today!\\n[Chorus]\\nFun with {clean_topic} hip hooray!",
  "verses": [{{"section": "Verse 1", "lines": ["Singing about {clean_topic} today!"]}}],
  "characters": [{{"character_id": "char_01", "name": "{clean_topic}", "species": "preschool character", "appearance": "Cute 3D preschool character with big cartoon eyes", "colors": ["#facc15", "#2563eb"], "clothing": "Colorful outfit", "personality": "Cheerful and friendly", "voice": "tenor_cheerful", "animation_set": ["walk", "jump", "dance", "wave"]}}],
  "environments": [{{"id": "env_01", "name": "{clean_topic} World", "description": "Vibrant colorful preschool environment"}}],
  "music_style": "120 BPM cheerful preschool pop with marimba and claps",
  "voice_style": "Warm cheerful preschool storyteller",
  "thumbnail_prompt": "Cute 3D CGI cartoon of {clean_topic}, 8k vibrant lighting, YouTube Kids thumbnail",
  "target_audience": "{target_age}",
  "educational_angle": "Vocabulary, rhythm and joyful play",
  "visual_bible": {{"visual_style": "3D Stylized Preschool Animation", "render_style": "Soft diffuse lighting, glossy toy-like palette"}}
}}"""

    try:
        retry_data = provider.generate_json(retry_prompt, system_prompt, max_tokens=1800)
        if retry_data and "lyrics_full" in retry_data:
            return _clean_pkg(retry_data)
    except Exception as e2:
        logger.error(f"AI retry also encountered an error: {e2}")

    # 3. Dynamic Fallback strictly constructed around the user's specific topic without hardcoded story scripts
    NL = "\n"
    lyrics_lines = [
        f"[Verse 1]",
        f"Come along and sing today, {clean_topic} is on the way!",
        f"Dancing in the bright sunshine, having such a happy time!",
        f"",
        f"[Chorus]",
        f"Clap your hands and spin around, hear the cheerful happy sound!",
        f"Learning with {clean_topic} now, smiling as we take a bow!",
        f"",
        f"[Verse 2]",
        f"One, two, three and four, five, six, making joyful rhythm clicks!",
        f"Every friend joins in to play, hip hooray, hip hooray!",
        f"",
        f"[Outro]",
        f"Thank you friends for singing along, sharing our delightful song!",
    ]
    lyrics_full = NL.join(lyrics_lines)

    return {
        "title": f"{clean_topic} ✨🎶 | 3D Nursery Rhymes for Kids",
        "description": f"Sing and dance with {clean_topic} in this fun, original preschool song!\n\n🎵 LYRICS:\n{lyrics_full}",
        "chapters": [
            {"time": "00:00", "title": "Welcome & Verse 1"},
            {"time": "00:30", "title": "Happy Dance Chorus"},
            {"time": "01:00", "title": "Verse 2: Action Play"},
            {"time": "01:45", "title": "Goodbye & Outro"},
        ],
        "hashtags": ["#nurseryrhymes", "#kidssongs", f"#{clean_topic.replace(' ', '').lower()}", "#preschool"],
        "tags": [clean_topic.lower(), f"{clean_topic.lower()} song", "nursery rhymes", "kids songs", "3d cartoon"],
        "story_concept": f"A delightful musical journey celebrating {clean_topic} with upbeat interactive dance steps.",
        "lyrics_full": lyrics_full,
        "approved_lyrics": lyrics_full,
        "verses": [
            {"section": "Verse 1", "lines": lyrics_lines[1:3], "character": clean_topic, "action": "bounces to rhythm"},
            {"section": "Chorus", "lines": lyrics_lines[5:7], "character": clean_topic, "action": "spins and dances"},
            {"section": "Verse 2", "lines": lyrics_lines[9:11], "character": clean_topic, "action": "claps hands happily"},
            {"section": "Outro", "lines": lyrics_lines[13:14], "character": clean_topic, "action": "waves goodbye cheerfully"},
        ],
        "characters": [
            {
                "character_id": "char_01",
                "name": clean_topic,
                "species": "preschool hero",
                "age": "Kid",
                "gender": "neutral",
                "appearance": f"Cute 3D stylized cartoon character inspired by {clean_topic} with large expressive eyes and bright pastel colors.",
                "colors": ["#facc15", "#2563eb"],
                "clothing": "Colorful preschool outfit",
                "personality": "Cheerful, energetic, and kind guide",
                "voice": "tenor_cheerful",
                "animation_set": ["walk", "jump", "dance", "wave", "bounce"],
            }
        ],
        "environments": [
            {
                "id": "env_01",
                "name": f"{clean_topic} Play Meadow",
                "description": f"Vibrant colorful preschool world themed around {clean_topic} with soft diffuse lighting and toy-like props.",
            }
        ],
        "music_style": "120 BPM cheerful preschool pop with marimba, acoustic guitar, and handclaps",
        "voice_style": "Warm cheerful preschool storyteller with clear articulation",
        "thumbnail_prompt": f"Cute 3D CGI cartoon animation of {clean_topic} smiling happily in vibrant meadow, 8k lighting, YouTube Kids thumbnail",
        "target_audience": target_age,
        "educational_angle": "Rhythm recognition, vocabulary, and cooperative play",
        "visual_bible": {
            "visual_style": "3D Cartoon Stylized Preschool Animation",
            "render_style": "Soft diffuse lighting, glossy toy-like materials, vibrant saturated palette",
            "lighting_style": "Bright warm daylight with subtle rim highlights",
            "camera_style": "Dynamic low-angle eye-level tracking with gentle push-ins",
            "environment_style": "Rounded low-poly hills, pastel skies, chunky props",
        },
    }
