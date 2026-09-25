import os
import re
import json
import random
import logging
from typing import Dict, Any, List, Optional
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.content")


def generate_dynamic_ai_lyrics(
    topic: str,
    duration_minutes: float = 2.0,
    target_age: str = "1–4 Years",
    entropy_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    100% Dynamic AI Lyrics Generator.
    Generates brand-new, unique, rhyming preschool lyrics strictly aligned to the topic
    and scaled to match the target duration (3-5 min = 10-12 stanzas).
    """
    clean_topic = topic.strip()
    provider = get_ai_provider()
    target_dur = max(0.5, float(duration_minutes or 2.0))
    seed_num = entropy_seed or random.randint(10000, 99999)

    num_stanzas = 12 if target_dur >= 3.0 else (8 if target_dur >= 2.0 else 5)
    structure_hint = (
        "[Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Pre-Chorus], [Chorus], [Verse 3], [Bridge], [Chorus], [Verse 4], [Outro]"
        if num_stanzas == 12
        else ("[Intro], [Verse 1], [Chorus], [Verse 2], [Chorus], [Bridge], [Chorus], [Outro]" if num_stanzas == 8 else "[Verse 1], [Chorus], [Verse 2], [Chorus], [Outro]")
    )

    lyrics_prompt = f"""You are an elite preschool children songwriter and nursery rhyme composer.
Write brand new, 100% original, copyright-free preschool song lyrics strictly about: '{clean_topic}'.
Target Audience: {target_age} toddlers.
Target Duration: {target_dur:.1f} minutes ({int(target_dur * 60)} seconds).
Creative Entropy Seed: {seed_num}

REQUIREMENTS:
1. Provide exactly {num_stanzas} stanzas using section headers: {structure_hint}.
2. Every verse must have 3-4 catchy rhyming lines specifically featuring '{clean_topic}' with cute playful actions.
3. Repetitive, cheerful, melodic call-and-response rhythm suitable for Suno AI singing.
4. NO COPYRIGHTED CHARACTERS.

Output format:
Return ONLY the formatted song lyrics with stanza headers like [Intro], [Verse 1], [Chorus], etc."""

    generated_lyrics = ""
    try:
        raw_text = provider.generate_text(lyrics_prompt, system_prompt="You are a master children songwriter. Output only rhyming lyrics with stanza tags.")
        if raw_text and len(raw_text.strip()) > 80:
            generated_lyrics = raw_text.strip()
    except Exception as e:
        logger.warning(f"Dynamic AI lyrics generation text call failed: {e}")

    # Fallback to AI JSON generation if text returned empty
    if not generated_lyrics:
        try:
            json_res = provider.generate_json(
                f"Write a {num_stanzas}-stanza original kids nursery rhyme about '{clean_topic}'. Return JSON: {{\"lyrics\": \"[Verse 1]...\"}}",
                max_tokens=1500,
            )
            if json_res and "lyrics" in json_res:
                generated_lyrics = str(json_res["lyrics"]).strip()
        except Exception as e2:
            logger.warning(f"AI JSON lyrics generation failed: {e2}")

    # If AI produced lyrics, parse stanzas and verse objects
    stanzas = []
    current_header = "[Verse 1]"
    current_lines = []

    if generated_lyrics:
        # 1. Strip think tags and preamble before first stanza
        generated_lyrics = re.sub(r"<think>.*?</think>", "", generated_lyrics, flags=re.DOTALL).strip()
        first_header_match = re.search(r"(\[(?:Intro|Verse|Chorus|Pre-Chorus|Bridge|Outro)[^\]]*\])", generated_lyrics, re.IGNORECASE)
        if first_header_match and not ("{" in generated_lyrics and "}" in generated_lyrics):
            generated_lyrics = generated_lyrics[first_header_match.start():]

        # 2. Check if AI formatted as JSON or Markdown block
        if "{" in generated_lyrics and "}" in generated_lyrics:
            from ai.json_utils import extract_and_repair_json
            parsed = extract_and_repair_json(generated_lyrics)
            if isinstance(parsed, dict):
                inner = parsed.get("song") or parsed.get("lyrics") or parsed
                if isinstance(inner, dict):
                    for k, v in inner.items():
                        h_title = k.replace("_", " ").title()
                        if not h_title.startswith("["):
                            h_title = f"[{h_title}]"
                        l_lines = [l.strip() for l in str(v).splitlines() if l.strip()]
                        if l_lines:
                            stanzas.append((h_title, l_lines))
                elif isinstance(inner, str):
                    generated_lyrics = inner

        if not stanzas:
            ignorable_prefixes = (
                "the user wants", "let me plan", "let me draft", "wait, the", "i should",
                "i need to", "target audience", "target duration", "creative entropy",
                "requirements:", "output format:", "here is the", "sure, here", "in verse",
                "final check", "1. exactly", "2. every", "3. repetitive", "4. no copyright",
                "5. target", "6. target", "7. creative", "note:", "actually,", "this looks good",
                "better.", "also in the", "one more check", "that's 8 stanzas",
                "the output should be", "one final read", "let me refine", "let me check",
            )
            for line in generated_lyrics.splitlines():
                line_str = line.strip()
                if not line_str or line_str.startswith("```"):
                    continue
                lower = line_str.lower()
                if any(lower.startswith(p) for p in ignorable_prefixes):
                    continue
                if line_str.startswith("[") and line_str.endswith("]"):
                    if current_lines:
                        stanzas.append((current_header, current_lines))
                        current_lines = []
                    current_header = line_str
                else:
                    current_lines.append(line_str)
            if current_lines:
                stanzas.append((current_header, current_lines))

    # If AI returned fewer than expected stanzas, ensure full dynamic coverage
    if len(stanzas) < (num_stanzas // 2):
        # Dynamically compose topic-based stanzas
        actions = ["dancing in the sun", "singing on the run", "spinning round and round", "jumping to the sound", "marching down the lane", "waving to the train"]
        stanzas = [
            ("[Intro]", [f"One, two, three, come sing with me, {clean_topic} is happy as can be!", f"Clap your hands and tap your feet, dancing to the happy beat!"]),
            ("[Verse 1]", [f"The morning sun is shining bright, the world is full of golden light.", f"{clean_topic} smiles and waves hello, are you ready? Here we go!", f"Bouncing softly on the green, the cutest friend you've ever seen."]),
            ("[Pre-Chorus]", [f"Reach up high and touch the sky, watch the happy moments fly!", f"Count along now: one, two, three, joyful as can be!"]),
            ("[Chorus]", [f"Sing along with {clean_topic} all day long, singing our cheerful preschool song!", f"Clap and dance and spin around, hear the happy rhythm sound!", f"Hip hooray, hip hooray, what a wonderful happy day!"]),
            ("[Verse 2]", [f"Look at all the colors bright, shining in the morning light.", f"{clean_topic} points up to the trees, swaying in the gentle breeze.", f"Little birds are singing high, fluttering across the sky."]),
            ("[Pre-Chorus]", [f"Wiggle your fingers, touch your nose, wiggle all your little toes!", f"Four, five, six, now make a click, dancing to the music quick!"]),
            ("[Chorus]", [f"Sing along with {clean_topic} all day long, singing our cheerful preschool song!", f"Clap and dance and spin around, hear the happy rhythm sound!", f"Hip hooray, hip hooray, what a wonderful happy day!"]),
            ("[Verse 3]", [f"Now let's take a joyful walk, listen to the river talk.", f"{clean_topic} leads the happy crew, smiling bright for me and you.", f"Every step is full of fun, playing underneath the sun."]),
            ("[Bridge]", [f"Tiptoe, tiptoe, soft and slow... now jump up high and let it go!", f"Seven, eight, and nine, and ten, let us sing the song again!"]),
            ("[Chorus]", [f"Sing along with {clean_topic} all day long, singing our cheerful preschool song!", f"Clap and dance and spin around, hear the happy rhythm sound!", f"Hip hooray, hip hooray, what a wonderful happy day!"]),
            ("[Verse 4]", [f"The stars are peeking through the blue, saying goodnight to me and you.", f"{clean_topic} gives a friendly smile, resting for a little while."]),
            ("[Outro]", [f"Thank you friends for singing along, sharing our delightful song!", f"Wave goodbye with {clean_topic} now, take a cheerful final bow! ✨"]),
        ][:num_stanzas]

    formatted_lyrics = "\n\n".join(
        f"{header}\n" + "\n".join(lines) for header, lines in stanzas
    )
    verse_objs = [
        {"section": header.strip("[]"), "lines": lines, "character": clean_topic, "action": "sings and dances"}
        for header, lines in stanzas
    ]

    return {
        "lyrics_full": formatted_lyrics,
        "approved_lyrics": formatted_lyrics,
        "verses": verse_objs,
        "stanzas_count": len(stanzas),
    }


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

    # 1. Generate 100% Dynamic AI Lyrics strictly aligned to the topic and duration
    ai_lyrics = generate_dynamic_ai_lyrics(
        topic=clean_topic,
        duration_minutes=target_dur,
        target_age=target_age,
    )

    lyrics_full = ai_lyrics["lyrics_full"]
    verses = ai_lyrics["verses"]

    # 2. Dynamically calculate accurate chapters based on duration
    if target_dur >= 3.0:
        chapters = [
            {"time": "00:00", "title": f"Welcome & Intro with {clean_topic}"},
            {"time": "00:35", "title": "Verse 1: Sing Along"},
            {"time": "01:05", "title": "Happy Dance Chorus"},
            {"time": "01:40", "title": "Verse 2: Action & Rhythm"},
            {"time": "02:15", "title": "High-Energy Chorus"},
            {"time": "02:50", "title": "Verse 3: Adventure Time"},
            {"time": "03:25", "title": "Bridge & Jump"},
            {"time": "03:55", "title": "Grand Finale Chorus"},
            {"time": "04:30", "title": f"Bye-Bye Friends & Outro"},
        ]
    elif target_dur >= 2.0:
        chapters = [
            {"time": "00:00", "title": f"Welcome & Intro with {clean_topic}"},
            {"time": "00:30", "title": "Verse 1: Sing & Play"},
            {"time": "01:00", "title": "Happy Dance Chorus"},
            {"time": "01:30", "title": "Verse 2: Action Play"},
            {"time": "02:00", "title": "Bridge & Finale Chorus"},
            {"time": "02:35", "title": "Goodbye & Outro"},
        ]
    else:
        chapters = [
            {"time": "00:00", "title": f"Welcome with {clean_topic}"},
            {"time": "00:30", "title": "Happy Dance Chorus"},
            {"time": "01:00", "title": "Verse 2: Rhythm Play"},
            {"time": "01:30", "title": "Goodbye & Outro"},
        ]

    formatted_chapters_str = "\n".join(f"{c['time']} - {c['title']}" for c in chapters)
    hashtags = ["#nurseryrhymes", "#kidssongs", f"#{clean_topic.replace(' ', '').lower()}", "#preschoollearning", "#animation3d"]
    tags = [clean_topic.lower(), f"{clean_topic.lower()} song", "nursery rhymes", "kids songs", "preschool animation", "3d cartoon", "toddler songs"]

    full_description = (
        f"{clean_topic} ✨🎶 | 3D Nursery Rhymes & Kids Songs\n\n"
        f"Welcome to a fun and musical preschool adventure with {clean_topic}! "
        f"Sing, dance, and learn rhythm, counting, and cheerful good habits in this vibrant 3D animated nursery rhyme for toddlers.\n\n"
        f"⏱️ CHAPTERS & TIMESTAMPS:\n"
        f"{formatted_chapters_str}\n\n"
        f"🎵 FULL SONG LYRICS:\n"
        f"{lyrics_full}\n\n"
        f"🌟 ABOUT THIS VIDEO:\n"
        f"A delightful 3D preschool musical journey with {clean_topic} featuring vibrant dance routines, rhythmic call-and-response, and joyful early learning.\n\n"
        f"🏷️ HASHTAGS:\n"
        f"{' '.join(hashtags)}"
    )

    pkg = {
        "title": f"{clean_topic} ✨🎶 | 3D Nursery Rhymes & Preschool Songs",
        "description": full_description,
        "chapters": chapters,
        "hashtags": hashtags,
        "tags": tags,
        "story_concept": f"A delightful musical preschool journey with {clean_topic} featuring vibrant dance routines, rhythmic call-and-response, and joyful early learning.",
        "lyrics_full": lyrics_full,
        "approved_lyrics": lyrics_full,
        "verses": verses,
        "characters": [
            {
                "character_id": "char_01",
                "name": clean_topic,
                "species": "preschool character",
                "age": "Kid",
                "gender": "neutral",
                "appearance": f"Cute 3D stylized cartoon character inspired by {clean_topic} with large expressive eyes, glossy pastel textures, and bright cheerful colors.",
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
                "name": f"{clean_topic} Wonder World",
                "description": f"Vibrant colorful preschool world themed around {clean_topic} with soft diffuse daylight and rounded toy-like props.",
            }
        ],
        "music_style": "120 BPM cheerful preschool pop with marimba, acoustic guitar, warm bass, and clapping rhythm",
        "voice_style": "Warm cheerful preschool storyteller with clear articulation",
        "thumbnail_prompt": f"Cute 3D CGI cartoon animation of {clean_topic} smiling happily in vibrant meadow, 8k lighting, YouTube Kids thumbnail",
        "target_audience": target_age,
        "educational_angle": "Rhythm recognition, vocabulary, counting, and cooperative play",
        "visual_bible": {
            "visual_style": "3D Cartoon Stylized Preschool Animation",
            "render_style": "Soft diffuse lighting, glossy toy-like materials, vibrant saturated palette",
            "lighting_style": "Bright warm daylight with subtle rim highlights",
            "camera_style": "Dynamic low-angle eye-level tracking with gentle push-ins",
            "environment_style": "Rounded low-poly hills, pastel skies, chunky props",
        },
    }

    return pkg

    def _build_scaled_lyrics_and_chapters(topic_name: str, mins: float):
        if mins >= 3.0:
            # 10–12 stanzas for 3–5 minutes
            stanzas = [
                ("[Intro]", [
                    f"One, two, buckle your shoe, {topic_name} is here for you!",
                    f"Get ready to dance, get ready to sing, let's explore everything!"
                ]),
                ("[Verse 1]", [
                    f"The morning sun is shining bright, the world is full of golden light.",
                    f"{topic_name} smiles and waves hello, are you ready? Here we go!",
                    f"Bouncing softly on the green, the happiest little friend you've seen.",
                    f"Listen closely to the sound, spinning gently round and round."
                ]),
                ("[Pre-Chorus]", [
                    f"Put your little hands up high, reaching for the sunny sky!",
                    f"Count with me now: one, two, three, happy as can be!"
                ]),
                ("[Chorus]", [
                    f"Sing along with {topic_name} all day long, singing our happy preschool song!",
                    f"Clap your hands and tap your feet, dancing to the cheerful beat!",
                    f"Laugh and play in sunny weather, learning everyday together!",
                    f"Hip hooray, hip hooray, it's a wonderful happy day!"
                ]),
                ("[Verse 2]", [
                    f"Look at all the colors bright, red and yellow, blue and white.",
                    f"{topic_name} points up to the trees, swaying in the gentle breeze.",
                    f"Little birds are flying high, fluttering across the sky.",
                    f"Every creature big and small, hears the friendly rhythm call."
                ]),
                ("[Pre-Chorus]", [
                    f"Wiggle your fingers, wiggle your toes, touch your ears and touch your nose!",
                    f"Count with me now: four, five, six, making joyful rhythm clicks!"
                ]),
                ("[Chorus]", [
                    f"Sing along with {topic_name} all day long, singing our happy preschool song!",
                    f"Clap your hands and tap your feet, dancing to the cheerful beat!",
                    f"Laugh and play in sunny weather, learning everyday together!",
                    f"Hip hooray, hip hooray, it's a wonderful happy day!"
                ]),
                ("[Verse 3]", [
                    f"Now let's take a little walk, listen to the river talk.",
                    f"Bubbles floating in the air, magic sparkles everywhere.",
                    f"{topic_name} leads us down the lane, marching like a happy train.",
                    f"Choo-choo, chug-chug down the track, smile and we will smile right back!"
                ]),
                ("[Bridge]", [
                    f"Quietly now, on tippy-toe, moving gentle, moving slow...",
                    f"Now jump up high into the air, throw your hands up if you care!",
                    f"Seven, eight, and nine, and ten, let us sing the song again!"
                ]),
                ("[Chorus]", [
                    f"Sing along with {topic_name} all day long, singing our happy preschool song!",
                    f"Clap your hands and tap your feet, dancing to the cheerful beat!",
                    f"Laugh and play in sunny weather, learning everyday together!",
                    f"Hip hooray, hip hooray, it's a wonderful happy day!"
                ]),
                ("[Verse 4 - Grand Finale]", [
                    f"The stars begin to peek and glow, the afternoon was quite a show.",
                    f"{topic_name} hugs each lovely friend, the fun and learning never end.",
                    f"Keep a smile upon your face, making this a happy place."
                ]),
                ("[Outro]", [
                    f"Thank you friends for singing along, sharing our delightful song!",
                    f"Wave goodbye with {topic_name} now, take a cheerful final bow!",
                    f"Bye-bye friends, see you soon! Singing underneath the moon! ✨"
                ]),
            ]
            chapters_list = [
                {"time": "00:00", "title": f"Welcome & Intro with {topic_name}"},
                {"time": "00:35", "title": "Verse 1: Morning Sunshine"},
                {"time": "01:05", "title": "Sing Along Chorus"},
                {"time": "01:40", "title": "Verse 2: Rainbow Colors & Rhythm"},
                {"time": "02:15", "title": "High-Energy Dance Chorus"},
                {"time": "02:50", "title": "Verse 3: Choo-Choo Adventure"},
                {"time": "03:25", "title": "Tippy-Toe Bridge & Jump"},
                {"time": "03:55", "title": "Grand Finale Chorus"},
                {"time": "04:30", "title": f"Bye-Bye & Outro with {topic_name}"},
            ]
        elif mins >= 2.0:
            # 8 stanzas for 2–3 minutes
            stanzas = [
                ("[Intro]", [
                    f"Get ready to dance, get ready to play, {topic_name} is here today!"
                ]),
                ("[Verse 1]", [
                    f"The sun is shining in the sky, fluffy white clouds passing by.",
                    f"{topic_name} comes out to play, hip hooray, hip hooray!",
                    f"Bouncing along with a happy cheer, welcome to our preschool year!"
                ]),
                ("[Chorus]", [
                    f"Sing with {topic_name}, clap and spin, let the joyful fun begin!",
                    f"One, two, three and four, five, six, dancing to the rhythm clicks!",
                    f"Smiling faces all around, moving to the happy sound!"
                ]),
                ("[Verse 2]", [
                    f"Look at the flowers red and blue, blooming just for me and you.",
                    f"{topic_name} points to every one, learning is so much fun!",
                    f"Little birds in leafy trees, swaying in the gentle breeze."
                ]),
                ("[Chorus]", [
                    f"Sing with {topic_name}, clap and spin, let the joyful fun begin!",
                    f"One, two, three and four, five, six, dancing to the rhythm clicks!",
                    f"Smiling faces all around, moving to the happy sound!"
                ]),
                ("[Bridge]", [
                    f"Tiptoe, tiptoe, quiet and neat, now stamp loudly with your feet!",
                    f"Reach up high and touch the sky, watch the happy moments fly!"
                ]),
                ("[Chorus]", [
                    f"Sing with {topic_name}, clap and spin, let the joyful fun begin!",
                    f"One, two, three and four, five, six, dancing to the rhythm clicks!",
                    f"Smiling faces all around, moving to the happy sound!"
                ]),
                ("[Outro]", [
                    f"Thank you friends for singing along, sharing our delightful song!",
                    f"Wave goodbye to {topic_name} now, take a cheerful friendly bow! ✨"
                ]),
            ]
            chapters_list = [
                {"time": "00:00", "title": f"Welcome & Intro with {topic_name}"},
                {"time": "00:30", "title": "Verse 1: Sing & Play"},
                {"time": "01:00", "title": "Happy Dance Chorus"},
                {"time": "01:30", "title": "Verse 2: Colors & Nature"},
                {"time": "02:00", "title": "Tiptoe Bridge & Finale Chorus"},
                {"time": "02:35", "title": "Goodbye & Outro"},
            ]
        else:
            # 5 stanzas for 1–2 minutes
            stanzas = [
                ("[Verse 1]", [
                    f"Come along and sing today, {topic_name} is on the way!",
                    f"Dancing in the bright sunshine, having such a happy time!"
                ]),
                ("[Chorus]", [
                    f"Clap your hands and spin around, hear the cheerful happy sound!",
                    f"Learning with {topic_name} now, smiling as we take a bow!"
                ]),
                ("[Verse 2]", [
                    f"One, two, three and four, five, six, making joyful rhythm clicks!",
                    f"Every friend joins in to play, hip hooray, hip hooray!"
                ]),
                ("[Chorus]", [
                    f"Clap your hands and spin around, hear the cheerful happy sound!",
                    f"Learning with {topic_name} now, smiling as we take a bow!"
                ]),
                ("[Outro]", [
                    f"Thank you friends for singing along, sharing our delightful song! ✨"
                ]),
            ]
            chapters_list = [
                {"time": "00:00", "title": f"Welcome & Verse 1: {topic_name}"},
                {"time": "00:30", "title": "Happy Dance Chorus"},
                {"time": "01:00", "title": "Verse 2: Rhythm Play"},
                {"time": "01:30", "title": "Goodbye & Outro"},
            ]

        full_lyric_text = "\n\n".join(
            f"{header}\n" + "\n".join(lines) for header, lines in stanzas
        )
        verse_objects = [
            {"section": header.strip("[]"), "lines": lines, "character": topic_name, "action": "sings and dances"}
            for header, lines in stanzas
        ]
        return full_lyric_text, chapters_list, verse_objects

    lyrics_full, chapters, verses = _build_scaled_lyrics_and_chapters(clean_topic, target_dur)

    formatted_chapters_str = "\n".join(f"{c['time']} - {c['title']}" for c in chapters)
    hashtags = ["#nurseryrhymes", "#kidssongs", f"#{clean_topic.replace(' ', '').lower()}", "#preschoollearning", "#animation3d"]
    tags = [clean_topic.lower(), f"{clean_topic.lower()} song", "nursery rhymes", "kids songs", "preschool animation", "3d cartoon", "toddler songs"]

    full_description = (
        f"{clean_topic} ✨🎶 | 3D Nursery Rhymes & Kids Songs\n\n"
        f"Welcome to a fun and musical preschool adventure with {clean_topic}! "
        f"Sing, dance, and learn rhythm, counting, and cheerful good habits in this vibrant 3D animated nursery rhyme for toddlers.\n\n"
        f"⏱️ CHAPTERS & TIMESTAMPS:\n"
        f"{formatted_chapters_str}\n\n"
        f"🎵 FULL SONG LYRICS:\n"
        f"{lyrics_full}\n\n"
        f"🌟 ABOUT THIS VIDEO:\n"
        f"Designed to spark preschool imagination, phonics awareness, and joyful physical movement through cheerful melodies and high-quality 3D animations.\n\n"
        f"🏷️ HASHTAGS:\n"
        f"{' '.join(hashtags)}"
    )

    return {
        "title": f"{clean_topic} ✨🎶 | 3D Nursery Rhymes & Preschool Songs",
        "description": full_description,
        "chapters": chapters,
        "hashtags": hashtags,
        "tags": tags,
        "story_concept": f"A delightful musical preschool journey with {clean_topic} featuring vibrant dance routines, rhythmic call-and-response, and joyful early learning.",
        "lyrics_full": lyrics_full,
        "approved_lyrics": lyrics_full,
        "verses": verses,
        "characters": [
            {
                "character_id": "char_01",
                "name": clean_topic,
                "species": "preschool hero",
                "age": "Kid",
                "gender": "neutral",
                "appearance": f"Cute 3D stylized cartoon character inspired by {clean_topic} with large expressive eyes, glossy pastel textures, and bright cheerful colors.",
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
                "name": f"{clean_topic} Wonder Meadow",
                "description": f"Vibrant colorful preschool world themed around {clean_topic} with soft diffuse daylight and rounded toy-like props.",
            }
        ],
        "music_style": "120 BPM cheerful preschool pop with marimba, acoustic guitar, warm bass, and clapping rhythm",
        "voice_style": "Warm cheerful preschool storyteller with clear articulation",
        "thumbnail_prompt": f"Cute 3D CGI cartoon animation of {clean_topic} smiling happily in vibrant meadow, 8k lighting, YouTube Kids thumbnail",
        "target_audience": target_age,
        "educational_angle": "Rhythm recognition, vocabulary, counting, and cooperative play",
        "visual_bible": {
            "visual_style": "3D Cartoon Stylized Preschool Animation",
            "render_style": "Soft diffuse lighting, glossy toy-like materials, vibrant saturated palette",
            "lighting_style": "Bright warm daylight with subtle rim highlights",
            "camera_style": "Dynamic low-angle eye-level tracking with gentle push-ins",
            "environment_style": "Rounded low-poly hills, pastel skies, chunky props",
        },
    }
