import re
import json
import logging
from typing import Dict, Any, List, Optional
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.content")


def generate_content_package(topic: str, video_type: str = "Nursery Rhyme", target_age: str = "1–4 Years") -> Dict[str, Any]:
    """
    Generates a complete kids content package from the selected topic.
    Returns:
    - title
    - description
    - chapters
    - hashtags
    - tags
    - story_concept
    - lyrics_full & verses (SOURCE OF TRUTH)
    - characters (Character Bible)
    - environments
    - music_style
    - voice_style
    - thumbnail_prompt
    - target_audience
    - educational_angle
    - visual_bible
    """
    clean_topic = topic.strip().capitalize()
    provider = get_ai_provider()

    prompt = f"""Generate a comprehensive, production-ready Kids/Nursery Rhyme Content Package for: '{clean_topic}'.
Target Audience: {target_age} preschoolers.
Format: {video_type}.
Style: High-energy sing-along with cute 3D Pixar/Cocomelon cartoon visuals.

Return a valid JSON object with the following EXACT structure:
{{
  "title": "Catchy YouTube Kids Title with Emojis",
  "description": "Engaging description including lyrics and call-to-actions",
  "chapters": [
    {{"time": "00:00", "title": "Welcome & Introduction"}},
    {{"time": "00:15", "title": "Verse 1: Sing Along"}},
    {{"time": "00:30", "title": "Happy Dance Chorus"}},
    {{"time": "00:45", "title": "Verse 2: Action Play"}},
    {{"time": "01:00", "title": "Outro & Goodbye"}}
  ],
  "hashtags": ["#nurseryrhymes", "#kidssongs", "#preschoollearning"],
  "tags": ["high-volume", "search-keywords", "youtube-studio"],
  "story_concept": "Detailed 2-3 sentence narrative describing character journey and actions",
  "lyrics_full": "Complete formatted lyrics with stanza tags [Verse 1], [Chorus], [Verse 2], [Outro]",
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
      "name": "Character Name",
      "species": "animal / vehicle / child / celestial",
      "age": "Kid / Preschooler",
      "gender": "neutral / boy / girl",
      "appearance": "Detailed 3D low-poly rounded description",
      "colors": ["#hex1", "#hex2"],
      "clothing": "Description of clothing / accessories",
      "face": "Big cartoon eyes with specular highlights, rosy cheeks, warm smile",
      "personality": "Cheerful, energetic, kind",
      "voice": "tenor_cheerful / soprano_gentle",
      "animation_set": ["walk", "jump", "dance", "wave", "bounce"]
    }}
  ],
  "environments": [
    {{
      "id": "env_01",
      "name": "Sunny Meadow",
      "description": "Vibrant emerald grass, colorful daisies, fluffy clouds under warm golden sunlight"
    }}
  ],
  "music_style": "120 BPM cheerful nursery pop with glockenspiel, marimba, warm bass, and clap rhythm",
  "voice_style": "Warm cheerful preschool storyteller with clear articulation",
  "thumbnail_prompt": "3D cute Pixar cartoon style of [Character] smiling happily in [Environment], 8k vibrant lighting, high CTR YouTube Kids thumbnail",
  "target_audience": "{target_age}",
  "educational_angle": "Rhythm recognition, phonics, color/object vocabulary and cooperative play",
  "visual_bible": {{
    "visual_style": "3D Cartoon Stylized Preschool",
    "render_style": "Soft diffuse lighting, glossy toy-like materials, vibrant saturated palette",
    "lighting_style": "Bright warm daylight with subtle rim highlights",
    "camera_style": "Dynamic low-angle eye-level tracking with gentle push-ins",
    "environment_style": "Rounded low-poly hills, pastel skies, chunky props"
  }}
}}"""

    system_prompt = "You are an elite preschool animation producer and songwriter for YouTube Kids (Cocomelon, Super Simple Songs). Produce top-tier rhyming stanzas with onomatopoeia and consistent character profiles. Output valid JSON only."

    try:
        data = provider.generate_json(prompt, system_prompt)
        if data and "lyrics_full" in data and "characters" in data and isinstance(data["characters"], list):
            logger.info(f"Generated complete content package via {provider.__class__.__name__}")
            # Ensure approved_lyrics is set to lyrics_full initially
            data["approved_lyrics"] = data["lyrics_full"]
            return data
    except Exception as e:
        logger.warning(f"AI content package generation failed, using procedural builder: {e}")

    return build_fallback_content_package(clean_topic, target_age)


def build_fallback_content_package(topic: str, target_age: str = "1–4 Years") -> Dict[str, Any]:
    """Guaranteed fallback content package engine."""
    clean_topic = topic.strip().capitalize()
    words = [w.lower() for w in re.findall(r"\b\w+\b", topic)]

    is_star = any(w in words for w in ["star", "moon", "night", "sky", "twinkle"])
    is_bus = any(w in words for w in ["bus", "car", "drive", "road", "wheel"])
    is_farm = any(w in words for w in ["cow", "duck", "farm", "sheep", "pig"])
    is_fruit = any(w in words for w in ["fruit", "apple", "banana", "berry"])
    is_dino = any(w in words for w in ["dino", "dinosaur", "rex"])

    if is_bus:
        char_id = "buster_bus"
        char_name = "Buster the Bus"
        species = "vehicle"
        title = "Wheels on the Yellow School Bus 🚌 | Fun Nursery Rhymes for Kids"
        env_name = "Sunny Town Road"
        v1_lines = [
            "The wheels on Buster Bus go round and round,",
            "Round and round, rolling all through the happy town!",
            "Buster Bus is smiling bright as he drives along the way,",
            "Taking all the cheerful friends to school and to play!",
        ]
        ch_lines = [
            "Beep beep goes the shiny horn, beep beep beep!",
            "Wipers on the windshield go swish swish swish!",
            "All the little children bounce up and down with cheer,",
            "Happy songs of laughter everywhere you hear!",
        ]
        v2_lines = [
            "The doors on the yellow bus go open and shut,",
            "Friendly little passengers waving as they strut!",
            "Up the hill and down the street, roll along the track,",
            "Buster Bus brings happiness there and brings it back!",
        ]
        outro_lines = [
            "Now we're at the playground, what a lovely ride,",
            "Everyone hop off and play on the giant slide!",
            "Thank you Buster Yellow Bus, wave goodbye with cheer,",
            "We'll see you tomorrow for another sunny year!",
        ]
    elif is_star:
        char_id = "twinkle_star"
        char_name = "Twinkle Star"
        species = "celestial"
        title = "Twinkle Twinkle Little Star ✨ Soothing 3D Bedtime Lullaby"
        env_name = "Midnight Starry Sky"
        v1_lines = [
            "Twinkle twinkle little star, shining in the sky so high,",
            "Like a sparkling diamond floating way up in the night sky!",
            "See the gentle crescent moon smiling with a gentle glow,",
            "Watching over sleeping dreams down on earth below!",
        ]
        ch_lines = [
            "Twinkle twinkle shine so bright, golden little light,",
            "Singing songs of peace and love all across the night!",
            "Drifting through the starry sky, dancing hand in hand,",
            "Welcome little dreamers to our happy starry land!",
        ]
        v2_lines = [
            "All the little colorful planets spinning round and round,",
            "Floating in the quiet dark without making a sound!",
            "Wave your hands up to the stars, make a lovely wish tonight,",
            "Everything is peaceful and everything is right!",
        ]
        outro_lines = [
            "Close your eyes and go to sleep, starry dreams are near,",
            "We will watch over you, safe and happy here!",
            "Goodnight to our little star, goodnight to the skies,",
            "Time for sweetest dreams to come as you close your eyes!",
        ]
    elif is_farm:
        char_id = "daisy_cow"
        char_name = "Daisy the Cow"
        species = "animal"
        title = "Old MacDonald's Happy Animal Farm 🚜 Sing-Along Kids Rhyme"
        env_name = "Sunny Farm Meadow"
        v1_lines = [
            "Old MacDonald had a farm, E-I-E-I-O!",
            "And on that farm he had a cow, E-I-E-I-O!",
            "With a moo moo here and a moo moo there,",
            "Daisy Cow is dancing with a flower in her hair!",
        ]
        ch_lines = [
            "Clap your hands with all our friends on the sunny farm,",
            "Every little animal has a friendly charm!",
            "Singing all together now, happy as can be,",
            "Living on the green farm, full of joy and free!",
        ]
        v2_lines = [
            "And on that farm he had a duck, E-I-E-I-O!",
            "With a quack quack here and a quack quack there,",
            "Splashing in the puddle pond without any care!",
            "Waddle waddle flap your wings, jump into the air!",
        ]
        outro_lines = [
            "Sun is setting on the barn, horses go to sleep,",
            "Cows and little yellow ducks, cozy fluffy sheep!",
            "Goodnight to Old MacDonald's farm, rest your sleepy head,",
            "Curled up warmly in your cozy little bed!",
        ]
    else:
        char_id = "toto_train"
        char_name = "Toto the Train"
        species = "vehicle"
        title = f"The Joyful {clean_topic} Song 🚂 | 3D Kids Nursery Rhymes"
        env_name = "Rainbow Railway Valley"
        v1_lines = [
            f"Choo choo comes the friendly train, {clean_topic} is here today,",
            "Singing cheerful nursery songs as we dance and play!",
            "Look at all our happy friends waving in the sun,",
            "Clap your hands and tap your feet, learning is so fun!",
        ]
        ch_lines = [
            "Chugga chugga choo choo, rolling down the track,",
            "Bringing lots of happiness there and bringing it back!",
            "Hear the shiny whistle blow, toot toot toot so clear,",
            "Every little friend is welcome, happy to be here!",
        ]
        v2_lines = [
            "Past the rolling green hills, under rainbow skies,",
            "Seeing all the butterflies flutter with surprise!",
            "Ring the shiny golden bell, ding dong ding dong chime,",
            "Every single journey is a happy storytime!",
        ]
        outro_lines = [
            "Now we're back at Station Home, wave goodbye with cheer,",
            "Thank you little friendly train for bringing sunshine here!",
            "Rest your wheels until tomorrow, have a restful night,",
            "Everything is peaceful and everything is bright!",
        ]

    verses = [
        {"section": "Verse 1", "lines": v1_lines, "character": char_name, "action": "bounces to rhythm"},
        {"section": "Chorus", "lines": ch_lines, "character": char_name, "action": "spins and dances"},
        {"section": "Verse 2", "lines": v2_lines, "character": char_name, "action": "waves and moves forward"},
        {"section": "Outro", "lines": outro_lines, "character": char_name, "action": "waves farewell under twilight stars"},
    ]

    lyrics_full = "\n\n".join(f"[{v['section']}]\n" + "\n".join(v["lines"]) for v in verses)

    return {
        "title": title,
        "description": f"Sing and dance with {char_name} in this joyful nursery rhyme about {clean_topic}!\n\n🎵 LYRICS:\n{lyrics_full}\n\n#nurseryrhymes #kidssongs #toddlers #preschool",
        "chapters": [
            {"time": "00:00", "title": "Welcome & Intro"},
            {"time": "00:15", "title": "Verse 1: Singing Along"},
            {"time": "00:30", "title": "Happy Dance Chorus"},
            {"time": "00:45", "title": "Verse 2: Fun Adventure"},
            {"time": "01:00", "title": "Outro & Goodbye"},
        ],
        "hashtags": ["#nurseryrhymes", "#kidssongs", f"#{clean_topic.replace(' ', '').lower()}", "#preschool"],
        "tags": [clean_topic.lower(), f"{clean_topic.lower()} song", "nursery rhymes", "kids songs", "toddler songs", "cocomelon style", "3d cartoon"],
        "story_concept": f"{char_name} takes young viewers on an imaginative musical journey through {env_name}, singing joyful songs and meeting friendly companions.",
        "lyrics_full": lyrics_full,
        "approved_lyrics": lyrics_full,
        "verses": verses,
        "characters": [
            {
                "character_id": char_id,
                "name": char_name,
                "species": species,
                "age": "Preschool Hero",
                "gender": "neutral",
                "appearance": f"Cute rounded 3D low-poly {species} with vibrant gloss materials, bright cartoon eyes, and playful proportions.",
                "colors": ["#facc15", "#2563eb", "#ef4444"],
                "clothing": "Cheerful striped conductor scarf or cozy accessories",
                "face": "Large expressive cartoon eyes with specular highlights, rosy cheeks, friendly curved smile",
                "personality": "Enthusiastic, caring, safe guide for toddlers",
                "voice": "tenor_cheerful",
                "animation_set": ["drive", "bounce", "wave", "spin", "jump"],
            }
        ],
        "environments": [
            {
                "id": "env_01",
                "name": env_name,
                "description": "Vibrant emerald grass, cartoon puffy trees, cheerful sunshine, and colorful flower meadows.",
            }
        ],
        "music_style": "120 BPM upbeat preschool melody with glockenspiel chimes, acoustic guitar, and clap percussion",
        "voice_style": "Warm cheerful preschool storyteller with animated enthusiasm",
        "thumbnail_prompt": f"Cute 3D Pixar cartoon of {char_name} smiling warmly in {env_name}, bright sunny morning lighting, saturated vivid colors, 8k render",
        "target_audience": target_age,
        "educational_angle": "Rhythm, cooperative play, and musical vocabulary",
        "visual_bible": {
            "visual_style": "3D Cartoon Stylized Preschool",
            "render_style": "Soft ambient occlusion, toy-like materials, vibrant saturated palette",
            "lighting_style": "Bright warm daylight with subtle rim highlights",
            "camera_style": "Dynamic low-angle eye-level tracking with gentle push-ins",
            "environment_style": "Rounded low-poly hills, pastel skies, chunky props",
        },
    }
