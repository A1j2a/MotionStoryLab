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
        "system": system_prompt or "You are an elite preschool animation and YouTube Kids SEO master (Cocomelon, Super Simple Songs). Return valid JSON only.",
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
            {"role": "system", "content": system_prompt or "You are an award-winning preschool animation creator (Cocomelon, Super Simple Songs). Return valid JSON only."},
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
    Generates original preschool nursery rhyme lyrics based on user topic.
    First tries external LLM (Ollama / OpenAI-compatible).
    Falls back to rich multi-theme procedural generation (Bus, Star, Farm, Fruit, Train, Animals).
    """
    topic_clean = topic.strip().capitalize()
    words = [w.lower() for w in re.findall(r"\b\w+\b", topic)]

    # 1. Try external AI if connected
    ai_result = call_llm_if_available(
        prompt=f"Generate original preschool nursery rhyme lyrics for toddlers about: '{topic_clean}'. Provide 4 verses (Verse 1, Chorus, Verse 2, Outro) with character actions. Format as JSON with keys: title, verses (list of objects with section, lines, character, action).",
        system_prompt="You are a professional children's TV songwriter (Cocomelon, Super Simple Songs). Output valid JSON only."
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

    # 2. Rich Multi-Theme Fallback Engine
    is_star = any(w in words for w in ["star", "moon", "night", "sky", "twinkle", "space", "planet"])
    is_bus = any(w in words for w in ["bus", "car", "drive", "road", "wheel", "traffic", "truck"])
    is_farm = any(w in words for w in ["cow", "duck", "farm", "sheep", "pig", "macdonald", "animal", "barn"])
    is_fruit = any(w in words for w in ["fruit", "apple", "banana", "berry", "vegetable", "food", "yummy"])
    is_train = any(w in words for w in ["train", "rail", "choo", "engine", "track", "steam", "chugga"])

    if is_star:
        title = "Twinkle Little Star and the Smiling Moon"
        verses = [
            {
                "section": "Verse 1",
                "lines": [
                    "Twinkle twinkle little star, shining in the sky so high,",
                    "Like a sparkling diamond floating way up in the night sky!",
                    "See the gentle crescent moon smiling with a gentle glow,",
                    "Watching over sleeping dreams down on earth below!",
                ],
                "character": "Twinkle Star",
                "action": "spins gently with golden sparkle rays",
            },
            {
                "section": "Chorus",
                "lines": [
                    "Twinkle twinkle shine so bright, golden little light,",
                    "Singing songs of peace and love all across the night!",
                    "Drifting through the starry sky, dancing hand in hand,",
                    "Welcome little dreamers to our happy starry land!",
                ],
                "character": "Smiling Moon",
                "action": "bounces softly with shining crescent halo",
            },
            {
                "section": "Verse 2",
                "lines": [
                    "All the little colorful planets spinning round and round,",
                    "Floating in the quiet dark without making a sound!",
                    "Wave your hands up to the stars, make a lovely wish tonight,",
                    "Everything is peaceful and everything is right!",
                ],
                "character": "Twinkle Star",
                "action": "twirls happily with companion planets",
            },
            {
                "section": "Outro",
                "lines": [
                    "Close your eyes and go to sleep, starry dreams are near,",
                    "We will watch over you, safe and happy here!",
                    "Goodnight to our little star, goodnight to the skies,",
                    "Time for sweetest dreams to come as you close your eyes!",
                ],
                "character": "All Friends",
                "action": "star and moon sway gently in lullaby harmony",
            },
        ]
    elif is_bus:
        title = "The Wheels on the Yellow School Bus"
        verses = [
            {
                "section": "Verse 1",
                "lines": [
                    "The wheels on Buster Bus go round and round,",
                    "Round and round, rolling all through the happy town!",
                    "Buster Bus is smiling bright as he drives along the way,",
                    "Taking all the cheerful friends to school and to play!",
                ],
                "character": "Buster the Bus",
                "action": "drives forward with rolling wheels and happy headlights",
            },
            {
                "section": "Chorus",
                "lines": [
                    "Beep beep goes the shiny horn, beep beep beep!",
                    "Wipers on the windshield go swish swish swish!",
                    "All the little children bounce up and down with cheer,",
                    "Happy songs of laughter everywhere you hear!",
                ],
                "character": "Buster the Bus",
                "action": "bounces to the 128 BPM swing rhythm",
            },
            {
                "section": "Verse 2",
                "lines": [
                    "The doors on the yellow bus go open and shut,",
                    "Friendly little passengers waving as they strut!",
                    "Up the hill and down the street, roll along the track,",
                    "Buster Bus brings happiness there and brings it back!",
                ],
                "character": "Buster the Bus",
                "action": "waves animated mirrors and blinks smiling eyes",
            },
            {
                "section": "Outro",
                "lines": [
                    "Now we're at the playground, what a lovely ride,",
                    "Everyone hop off and play on the giant slide!",
                    "Thank you Buster Yellow Bus, wave goodbye with cheer,",
                    "We'll see you tomorrow for another sunny year!",
                ],
                "character": "All Friends",
                "action": "waving goodbye from the bus stop playground",
            },
        ]
    elif is_farm:
        title = "Old MacDonald's Happy Animal Farm"
        verses = [
            {
                "section": "Verse 1",
                "lines": [
                    "Old MacDonald had a farm, E-I-E-I-O!",
                    "And on that farm he had a cow, E-I-E-I-O!",
                    "With a moo moo here and a moo moo there,",
                    "Daisy Cow is dancing with a flower in her hair!",
                ],
                "character": "Daisy Cow",
                "action": "bounces in the meadow and waves",
            },
            {
                "section": "Chorus",
                "lines": [
                    "Clap your hands with all our friends on the sunny farm,",
                    "Every little animal has a friendly charm!",
                    "Singing all together now, happy as can be,",
                    "Living on the green farm, full of joy and free!",
                ],
                "character": "Daisy Cow",
                "action": "rings cheerful cowbell and nods head",
            },
            {
                "section": "Verse 2",
                "lines": [
                    "And on that farm he had a duck, E-I-E-I-O!",
                    "With a quack quack here and a quack quack there,",
                    "Splashing in the puddle pond without any care!",
                    "Waddle waddle flap your wings, jump into the air!",
                ],
                "character": "Benny Duck",
                "action": "waddles and flaps yellow wings",
            },
            {
                "section": "Outro",
                "lines": [
                    "Sun is setting on the barn, horses go to sleep,",
                    "Cows and little yellow ducks, cozy fluffy sheep!",
                    "Goodnight to Old MacDonald's farm, rest your sleepy head,",
                    "Curled up warmly in your cozy little bed!",
                ],
                "character": "All Friends",
                "action": "waves goodbye under the golden sunset barn",
            },
        ]
    elif is_fruit:
        title = "The Yummy Dancing Fruits Song"
        verses = [
            {
                "section": "Verse 1",
                "lines": [
                    "Red Apple, Sweet Banana, dancing in the sun,",
                    "Yummy healthy fruits are so much happy fun!",
                    "Apples crunchy, apples sweet, tap your little feet,",
                    "Dancing all together to the joyful fruity beat!",
                ],
                "character": "Happy Apple",
                "action": "bounces on green meadow wearing leaf hat",
            },
            {
                "section": "Chorus",
                "lines": [
                    "Shake shake shake your little fruit, one and two and three,",
                    "Growing big and strong today, happy as can be!",
                    "Yummy in my tummy, healthy treats to eat,",
                    "Smiling fruit companions make every day so sweet!",
                ],
                "character": "Sunny Banana",
                "action": "hops and does the fruit dance twist",
            },
            {
                "section": "Verse 2",
                "lines": [
                    "Little purple grapes are jumping in a bunch,",
                    "Orange juice and strawberries ready for our lunch!",
                    "Spin around in circles, give a happy cheer,",
                    "Fruits are the best friends of all the children here!",
                ],
                "character": "Happy Apple",
                "action": "spins in a cheerful circle",
            },
            {
                "section": "Outro",
                "lines": [
                    "Eat your healthy colors every single day,",
                    "Now it's time to rest our feet after dance and play!",
                    "Wave goodbye to Apple, wave to Banana friend,",
                    "Our fruity happy story has reached a lovely end!",
                ],
                "character": "All Fruits",
                "action": "waving leaves and smiles in harmony",
            },
        ]
    elif is_train:
        title = "Chugga Chugga Choo Choo Train"
        verses = [
            {
                "section": "Verse 1",
                "lines": [
                    "Chugga chugga choo choo, rolling on the track,",
                    "Little Blue Train is moving there and back!",
                    "Hear the friendly whistle blow, toot toot toot so loud,",
                    "Puffing happy smoke rings up into the cloud!",
                ],
                "character": "Toto the Train",
                "action": "puffs steam rings and chugs down the tracks",
            },
            {
                "section": "Chorus",
                "lines": [
                    "All aboard the happy train, come along and play,",
                    "Singing cheerful nursery songs every single day!",
                    "Chugga chugga choo choo, rolling through the land,",
                    "Join our friendly circle and take my little hand!",
                ],
                "character": "Toto the Train",
                "action": "rotates red wheels with golden hubcaps",
            },
            {
                "section": "Verse 2",
                "lines": [
                    "Rolling past the flower fields, waving to the cow,",
                    "Daisy Cow says moo moo moo, wave hello right now!",
                    "Through the gentle tunnel and over hills of green,",
                    "Happiest little train that you have ever seen!",
                ],
                "character": "Daisy Cow",
                "action": "waves hello from the track meadow",
            },
            {
                "section": "Outro",
                "lines": [
                    "Train is rolling into station, sunset in the sky,",
                    "Thank you little engine, wave a sweet goodbye!",
                    "Rest your wheels until tomorrow, have a restful dream,",
                    "Goodnight to our friendly little locomotive team!",
                ],
                "character": "All Friends",
                "action": "everyone waves goodbye at the station",
            },
        ]
    else:
        title = topic_clean if len(topic_clean) < 40 else f"{topic_clean[:37]}..."
        verses = [
            {
                "section": "Verse 1",
                "lines": [
                    f"Welcome to our sunny world, bright and full of fun,",
                    f"Come and see the happy smile of the morning sun!",
                    f"{topic_clean} is what we love today,",
                    "Singing cheerful songs as we dance and play!",
                ],
                "character": "Sunny Character",
                "action": "bounces and smiles in the meadow",
            },
            {
                "section": "Chorus",
                "lines": [
                    "Clap your little hands now, one and two and three,",
                    "Join our friendly circle, happy as can be!",
                    "Singing our sweet nursery rhyme all the whole day through,",
                    "Smiling for our friends and for me and you!",
                ],
                "character": "Sunny Character",
                "action": "claps and dances with colorful stars",
            },
            {
                "section": "Verse 2",
                "lines": [
                    "Look at all the rainbow colors floating in the air,",
                    "Gentle little butterflies flying everywhere!",
                    "Spin around in circles, give a joyful cheer,",
                    "We are having so much fun with our companions here!",
                ],
                "character": "Rainbow Friend",
                "action": "spins around with butterflies",
            },
            {
                "section": "Outro",
                "lines": [
                    "Now it's time to wave goodbye to our sunny day,",
                    "We will meet again real soon to sing and dance and play!",
                    "Close your gentle eyes now, drift into your dream,",
                    "Sweet dreams to our happy playful team!",
                ],
                "character": "All Characters",
                "action": "waves goodbye under evening stars",
            },
        ]

    return {
        "title": title,
        "lyrics_full": "\n\n".join(
            f"[{v['section']}]\n" + "\n".join(v["lines"]) for v in verses
        ),
        "verses": verses,
    }


def generate_character_bible(topic: str) -> List[Dict[str, Any]]:
    """
    Generates consistent 3D Character Bible matching the topic theme.
    """
    words = [w.lower() for w in re.findall(r"\b\w+\b", topic)]
    if any(w in words for w in ["star", "moon", "night", "sky", "twinkle"]):
        return [
            {
                "id": "twinkle_star",
                "name": "Twinkle Star",
                "type": "celestial",
                "appearance": "Golden 5-pointed cute star with big anime cartoon eyes, rosy blush cheeks, and sparkling golden aura",
                "colors": ["#facc15", "#fde047", "#ffffff"],
                "personality": "Gentle, magical, and comforting",
                "age": "Preschool Star",
                "voice": "soprano_gentle",
                "animation_set": ["twirl", "sparkle", "bob", "smile"],
            },
            {
                "id": "smiling_moon",
                "name": "Smiling Moon",
                "type": "celestial",
                "appearance": "Cozy buttercup-yellow crescent moon wearing a cozy striped nightcap",
                "colors": ["#fef08a", "#60a5fa"],
                "personality": "Warm, sleepy, and reassuring",
                "age": "Parental Guide",
                "voice": "alto_warm",
                "animation_set": ["sway", "blink", "nod"],
            },
        ]
    elif any(w in words for w in ["bus", "car", "wheel", "drive"]):
        return [
            {
                "id": "buster_bus",
                "name": "Buster the Bus",
                "type": "vehicle",
                "appearance": "Cheerful canary-yellow school bus with animated windshield eyes, smiling grill, and bouncy suspension",
                "colors": ["#facc15", "#1e293b", "#dc2626"],
                "personality": "Enthusiastic, safe, and helpful",
                "age": "Preschool Hero",
                "voice": "tenor_cheerful",
                "animation_set": ["drive", "bounce", "beep", "blink"],
            },
        ]
    elif any(w in words for w in ["fruit", "apple", "banana"]):
        return [
            {
                "id": "happy_apple",
                "name": "Happy Apple",
                "type": "fruit",
                "appearance": "Glossy candy-red apple with cartoon eyes, green leaf hat, and bouncy shoes",
                "colors": ["#ef4444", "#22c55e", "#ffffff"],
                "personality": "Loves dancing, health, and exercise",
                "age": "Kid",
                "voice": "soprano_peppy",
                "animation_set": ["bounce", "spin", "jump"],
            },
            {
                "id": "sunny_banana",
                "name": "Sunny Banana",
                "type": "fruit",
                "appearance": "Smiling crescent banana that taps and twists with joyful rhythm",
                "colors": ["#facc15", "#a16207"],
                "personality": "Silly, musical, and playful",
                "age": "Kid",
                "voice": "alto_sweet",
                "animation_set": ["twist", "hop", "wave"],
            },
        ]
    elif any(w in words for w in ["cow", "duck", "farm", "sheep"]):
        return [
            {
                "id": "daisy_cow",
                "name": "Daisy the Cow",
                "type": "animal",
                "appearance": "Cute rounded black-and-white spotted calf with friendly blush cheeks and a shiny brass bell",
                "colors": ["#ffffff", "#1e293b", "#f43f5e"],
                "personality": "Playful, musical, and loves to dance",
                "age": "Kid",
                "voice": "alto_sweet",
                "animation_set": ["wave", "dance", "jump", "nod"],
            },
        ]
    else:
        return [
            {
                "id": "toto_train",
                "name": "Toto the Train",
                "type": "vehicle",
                "appearance": "Chunky cobalt blue steam locomotive with animated friendly eyes, cherry red wheels, and brass chimney",
                "colors": ["#2563eb", "#dc2626", "#eab308"],
                "personality": "Cheerful, energetic, and caring guide",
                "age": "Preschool Hero",
                "voice": "tenor_cheerful",
                "animation_set": ["drive", "bounce", "spin", "wave"],
            },
        ]


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
    verses: List[Dict[str, Any]],
    scenes: List[Dict[str, Any]],
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

#nurseryrhymes #kidssongs #toddlerlearning #preschoolcartoons #3danimation #cocomelon #supersimplesongs
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
        "super simple songs",
        "cocomelon style",
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
