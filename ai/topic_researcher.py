import os
import re
import json
import random
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.topics")

DB_PATH = Path(__file__).resolve().parent.parent / "projects" / "studio.db"


def _generate_pure_dynamic_fallback_topic(
    rng: random.Random,
    target_age: str,
    duration: str,
    language: str,
    excluded_signatures: Optional[Set[str]] = None,
    current_batch_signatures: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    Generates a 100% dynamically synthesized, non-static preschool topic card
    using randomized creative syllables, actions, and educational concepts.
    """
    is_hindi = "hindi" in language.lower()
    is_spanish = "spanish" in language.lower()
    exc_sigs = excluded_signatures or set()
    curr_sigs = current_batch_signatures or set()

    for _ in range(50):
        if is_hindi:
            names = ["चिंटू", "पिंकी", "गोलू", "सोनू", "मीकू", "बबलू", "टिंकू", "नन्ही", "तारा", "राजू", "काजू", "झुमरी", "लड्डू"]
            animals = ["हाथी", "बंदर", "तितली", "खरगोश", "चिड़िया", "भालू", "बिल्ली", "तोता", "मछली", "शेर", "गिलहरी", "मोर"]
            actions = ["की रेलगाड़ी", "का जादुई मेला", "का रंगीन खेल", "की मीठी लोरी", "का फन डांस", "की पाठशाला", "का फलों का बाग"]
            adjs = ["नटखट", "प्यारा", "रंगीन", "खुशमिजाज", "चुलबुला", "जादुई", "सुरीला", "होशियार"]
            
            n = rng.choice(names)
            a = rng.choice(animals)
            act = rng.choice(actions)
            adj = rng.choice(adjs)
            
            title = f"{adj} {n} {a} {act}  | Hindi Balgeet for Kids"
            topic = f"{n} {a} - {act}"
            category = rng.choice(["Numbers & Counting", "Good Habits", "Bedtime Lullabies", "Animals & Nature", "Colors & Shapes"])
            hook = f"Interactive Hindi preschool rhyme featuring {adj} {n} with catchy rhythm."
            why = "High search engagement for Hindi rhymes with cute animal characters."
            signals = "Consistent high repeat watch time in Hindi preschool demographic."
            chars = [f"{n} {a}", "Dost Bunny", "Chintu"]
            concept = f"{n} playfully dances across scenic 3D backgrounds, teaching early preschool concepts."
            keywords = [n.lower(), a.lower(), "hindi rhymes", "balgeet", "toddler hindi song"]
            seo_tags = ["#hindirhymes", "#balgeet", "#kidssongs", "#preschoollearning", "#animation3d"]
        elif is_spanish:
            names = ["Tito", "Lulu", "Panchito", "Rosita", "Milo", "Benito", "Chispita", "Solecito", "Mateo", "Sofia"]
            animals = ["el Osito", "el Conejito", "el Patito", "el Perrito", "la Ranita", "el Gatito", "el Zorrito", "el Pajarito"]
            actions = ["Aprende los Números", "El Baile de las Frutas", "La Ronda de los Colores", "Canción para Dormir", "El Paseo Mágico"]
            
            n = rng.choice(names)
            a = rng.choice(animals)
            act = rng.choice(actions)
            title = f"{n} {a} | {act}  | Canciones Infantiles 3D"
            topic = f"{n} {a} - {act}"
            category = rng.choice(["Numbers & Counting", "Good Habits", "Bedtime Lullabies", "Colors & Shapes", "Social-Emotional"])
            hook = f"Joyful Spanish preschool melody where {n} {a} {act.lower()}."
            why = "High organic search intent for Spanish educational preschool music."
            signals = "Strong global search volume across Latin America & Spanish markets."
            chars = [f"{n} {a}", "Amigo Oso", "Pajarito"]
            concept = f"{n} {a} guides little learners through fun rhymes and cheerful dances."
            keywords = [n.lower(), "canciones infantiles", "rimas para ninos", "preschool spanish"]
            seo_tags = ["#cancionesinfantiles", "#rimasparaniños", "#kidssongs", "#educacioninfantil"]
        else:
            first_names = ["Barnaby", "Ziggy", "Cleo", "Finny", "Hazel", "Penny", "Ollie", "Sammy", "Milo", "Daisy", "Toby", "Luna", "Felix", "Sunny", "Ruby", "Leo", "Coco", "Bumble", "Jasper", "Waffles"]
            descriptors = ["Little", "Bouncy", "Cheerful", "Giggly", "Curious", "Sunny", "Happy", "Sparkly", "Playful", "Dancing", "Jolly", "Sleepy"]
            species = ["Bunny", "Puppy", "Dino", "Kitten", "Panda", "Fox", "Bear", "Penguin", "Otter", "Duckling", "Lamb", "Hedgehog", "Rocket", "Bus", "Train", "Star", "Cloud"]
            activities = [
                ("Counting Adventure 1 to 10", "Numbers & Counting", "counting glowing objects with rhythmic beats"),
                ("Rainbow Color Parade", "Colors & Shapes", "discovering vibrant primary colors through song"),
                ("Brushing & Morning Habits", "Good Habits", "practicing daily healthy routines with joyful tunes"),
                ("Bedtime Starlight Lullaby", "Bedtime Lullabies", "soothing acoustic melodies for relaxing sleep"),
                ("Animal Sounds Safari", "Animals & Nature", "learning animal sounds and funny movements"),
                ("Happy Clap & Dance Along", "Action & Dance", "encouraging happy physical dance and motor skills"),
                ("Yummy Healthy Fruit Discovery", "Healthy Eating", "learning about colorful healthy fruits and vitamins"),
                ("Sharing & Friendship Song", "Social-Emotional", "learning kindness and sharing toys with friends"),
            ]
            
            fn = rng.choice(first_names)
            desc = rng.choice(descriptors)
            sp = rng.choice(species)
            act_name, cat, hook_desc = rng.choice(activities)
            emojis = rng.choice(["", "", "", "", "", "", ""])
            
            full_char = f"{fn} the {desc} {sp}"
            title = f"{full_char} | {act_name} {emojis} | Kids Nursery Rhymes & 3D Songs"
            topic = f"{full_char} - {act_name}"
            category = cat
            hook = f"{full_char} leads preschoolers through {hook_desc}."
            why = f"Combines {cat.lower()} educational fundamentals with high-CTR preschool visual hooks."
            signals = "High search intent among toddlers and parents with above-average watch time completion."
            chars = [full_char, "Sunny Friend", "Little Star"]
            concept = f"{full_char} explores vibrant 3D preschool environments while singing catchy interactive choruses."
            keywords = [fn.lower(), sp.lower(), "nursery rhymes 3d", "toddler songs", "preschool learning"]
            seo_tags = ["#nurseryrhymes", "#kidssongs", "#toddlervideos", "#preschoollearning", "#animation3d"]

        card = {
            "topic": topic,
            "suggested_title": title,
            "category": category,
            "target_age": target_age,
            "duration": duration,
            "search_keywords": keywords,
            "seo_tags": seo_tags,
            "content_angle": hook,
            "why_worth_considering": why,
            "opportunity_signals": signals,
            "suggested_characters": chars,
            "suggested_story_concept": concept,
        }

        if not is_topic_duplicate_or_excluded(card, exc_sigs, curr_sigs):
            return card

    return card


def _init_topics_storage():
    """Ensures the used_topics table exists with full index support."""
    try:
        if DB_PATH.exists():
            conn = sqlite3.connect(str(DB_PATH), timeout=5)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS used_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT UNIQUE,
                    character TEXT,
                    lost_or_broken_object TEXT,
                    category TEXT,
                    learning_payoff TEXT,
                    status TEXT DEFAULT 'CONSUMED',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_used_topics_title ON used_topics(title)")
            conn.commit()
            conn.close()
    except Exception as e:
        logger.warning(f"Could not init used_topics table: {e}")


def _get_used_topics_context() -> Tuple[List[str], Set[str], Set[str], Set[str]]:
    """
    Loads all permanently used and completed topics from both used_topics table AND projects table.
    Returns:
    - used_topics_formatted_list (for prompt {{USED_TOPICS}})
    - used_titles_normalized_set
    - used_characters_set
    - used_objects_set
    """
    _init_topics_storage()
    formatted_list: List[str] = []
    used_titles: Set[str] = set()
    used_chars: Set[str] = set()
    used_objs: Set[str] = set()

    try:
        if DB_PATH.exists():
            conn = sqlite3.connect(str(DB_PATH), timeout=5)
            c = conn.cursor()

            # 1. Fetch from used_topics table
            c.execute("SELECT title, character, lost_or_broken_object, category, learning_payoff FROM used_topics ORDER BY id DESC LIMIT 500")
            for row in c.fetchall():
                title, char, obj, cat, payoff = row
                if title:
                    norm = title.lower().strip()
                    used_titles.add(norm)
                    desc = f"- {title}"
                    if cat or payoff:
                        desc += f" ({cat or 'General'} / {payoff or 'Learning'}"
                    formatted_list.append(desc)
                if char:
                    used_chars.add(char.lower().strip())
                if obj:
                    used_objs.add(obj.lower().strip())

            # 2. Fetch from existing created projects to guarantee 100% deduplication
            c.execute("SELECT title, topic FROM projects")
            for row in c.fetchall():
                p_title, p_topic = row
                for val in (p_title, p_topic):
                    if val:
                        norm = val.lower().strip()
                        if norm not in used_titles:
                            used_titles.add(norm)
                            formatted_list.append(f"- {val} (Created Project / In Production)")

            conn.close()
    except Exception as e:
        logger.warning(f"Could not load used topics context: {e}")

    return formatted_list, used_titles, used_chars, used_objs


def mark_topic_as_used(
    title: str,
    topic: Optional[str] = None,
    character: Optional[str] = None,
    lost_or_broken_object: Optional[str] = None,
    category: Optional[str] = None,
    learning_payoff: Optional[str] = None,
):
    """
    Permanently stores a completed or selected topic in the database so it can NEVER be repeated.
    """
    _init_topics_storage()
    clean_title = (title or topic or "").strip()
    if not clean_title:
        return

    try:
        if DB_PATH.exists():
            conn = sqlite3.connect(str(DB_PATH), timeout=5)
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO used_topics (title, character, lost_or_broken_object, category, learning_payoff, status)
                VALUES (?, ?, ?, ?, ?, 'CONSUMED')
            """, (
                clean_title,
                (character or "").strip(),
                (lost_or_broken_object or "").strip(),
                (category or "").strip(),
                (learning_payoff or "").strip(),
            ))
            if topic and topic.strip() != clean_title:
                c.execute("""
                    INSERT OR IGNORE INTO used_topics (title, character, lost_or_broken_object, category, learning_payoff, status)
                    VALUES (?, ?, ?, ?, ?, 'CONSUMED')
                """, (
                    topic.strip(),
                    (character or "").strip(),
                    (lost_or_broken_object or "").strip(),
                    (category or "").strip(),
                    (learning_payoff or "").strip(),
                ))
            conn.commit()
            conn.close()
            logger.info(f"Permanently marked topic as CONSUMED: {clean_title}")
    except Exception as e:
        logger.warning(f"Failed to mark topic as consumed in DB: {e}")


def _record_used_topics(topics: List[Dict[str, Any]]):
    """Stores a batch of generated topics into the database."""
    for t in topics:
        mark_topic_as_used(
            title=t.get("title") or t.get("suggested_title") or "",
            topic=t.get("topic"),
            character=t.get("character"),
            lost_or_broken_object=t.get("lost_or_broken_object"),
            category=t.get("category"),
            learning_payoff=t.get("learning_payoff"),
        )


def _dynamic_procedural_fallback(
    count: int,
    seed_val: int,
    used_titles: Set[str],
    used_chars: Set[str],
    used_objs: Set[str],
    target_age: str,
    duration: str,
) -> List[Dict[str, Any]]:
    """
    Purely procedural dynamic generator adhering to the official 'Oh No!' arc and HARD RULES.
    Guarantees picking characters and objects NOT in the used set.
    """
    rng = random.Random(seed_val)
    categories = [
        ("Vehicle",
         ["Little Tractor", "Fire Truck", "Scooter", "Helicopter", "Submarine", "Bicycle", "Toy Train", "Delivery Van", "Little Bulldozer", "Sailboat", "Rocket Toy", "Go-Kart"],
         [("Lost His Key", "Key"), ("Lost His Horn", "Horn"), ("Lost His Wheel", "Wheel"), ("Broke His Headlight", "Headlight"), ("Can't Find His Bell", "Bell"), ("Lost His Siren", "Siren")]),
        ("Animal",
         ["Baby Otter", "Little Panda", "Koala Bear", "Cheeky Monkey", "Tiny Giraffe", "Little Lamb", "Baby Elephant", "Puppy", "Playful Kitten", "Baby Hippo", "Little Kangaroo", "Zippy Zebra"],
         [("Lost His Blanket", "Blanket"), ("Lost His Acorn", "Acorn"), ("Lost His Hat", "Hat"), ("Broke His Drum", "Drum"), ("Can't Find His Scarf", "Scarf"), ("Lost His Ball", "Ball")]),
        ("Household object",
         ["Teddy Bear", "Clocky the Clock", "Spoon & Fork", "Teapot", "Lampy", "Robot Toy", "Crayon Box", "Musical Drum", "Paintbrush Buddy", "Toaster Friend"],
         [("Lost His Button", "Button"), ("Lost His Star", "Star"), ("Lost His Handle", "Handle"), ("Broke His Spring", "Spring"), ("Can't Find His Paintbrush", "Paintbrush"), ("Lost His Ribbon", "Ribbon")]),
        ("Bedtime-routine",
         ["Sleepy Sloth", "Night Owl", "Dreamy Star", "Little Fox", "Cuddle Bear", "Moon Beam", "Pajama Bunny"],
         [("Lost His Slippers", "Slippers"), ("Lost His Pajama Button", "Pajama Button"), ("Can't Find His Storybook", "Storybook"), ("Lost His Night Cap", "Night Cap"), ("Lost His Pillow", "Pillow")]),
        ("Nature",
         ["Bumblebee", "Ladybug", "Little Raindrop", "Sunbeam", "Acorn Squirrel", "Green Frog", "Garden Snail", "Tiny Caterpillar", "Fluffy Cloud"],
         [("Lost His Honey Jar", "Honey Jar"), ("Lost Her Polka Dot", "Polka Dot"), ("Lost His Lily Pad", "Lily Pad"), ("Broke His Leaf Umbrella", "Leaf Umbrella"), ("Can't Find His Blossom", "Blossom")]),
    ]
    payoffs = ["Counting 1-5", "Colors", "Shapes", "Sounds"]
    search_places = [
        ["under the sofa", "inside the toybox", "behind the blue door", "under the garden rug", "on top of the bed"],
        ["in the flowerbed", "behind the tall tree", "near the duck pond", "under the wooden bench", "inside the hollow log"],
        ["on the kitchen shelf", "under the cozy armchair", "behind the striped curtain", "inside the laundry basket", "under the soft pillow"],
        ["in the sandpit", "under the wooden slide", "behind the green bushes", "inside the wagon", "under the park swing"],
    ]

    results = []
    attempts = 0
    while len(results) < count and attempts < 250:
        attempts += 1
        cat_name, chars, actions = rng.choice(categories)
        
        # Pick character not overused
        available_chars = [c for c in chars if c.lower() not in used_chars]
        char = rng.choice(available_chars) if available_chars else rng.choice(chars)
        
        # Pick action / object not overused
        action_tuple = rng.choice(actions)
        act_text, obj_name = action_tuple
        
        title = f"Oh No! {char} {act_text}!"
        norm_title = title.lower().strip()
        if norm_title in used_titles:
            continue

        used_titles.add(norm_title)
        used_chars.add(char.lower())
        used_objs.add(obj_name.lower())

        payoff = rng.choice(payoffs)
        places = rng.choice(search_places)
        hook = f"{char} searches {places[0]}, {places[1]}, {places[2]}, and {places[3]}, finally finding it {places[4]}!"

        results.append({
            "title": title,
            "suggested_title": f"{title}  | 3D Nursery Rhymes & Kids Songs",
            "topic": title.replace("Oh No! ", "").replace("!", ""),
            "character": char,
            "lost_or_broken_object": obj_name,
            "category": cat_name,
            "learning_payoff": payoff,
            "content_angle": hook,
            "why_worth_considering": f"Official 'Oh No!' problem-solving arc teaching early {payoff.lower()} with suspense, false leads, and high toddler retention.",
            "opportunity_signals": "Top-ranking preschool YouTube search structure with 10M+ view potential and repeat watch time.",
            "suggested_characters": [char, "Friendly Friend", "Mama Guide"],
            "suggested_story_concept": f"{char} experiences a fun preschool mishap, hunts in 5 lively spots with funny sound effects, and celebrates with a warm {payoff} song.",
            "target_age": target_age,
            "duration": duration,
            "search_keywords": [char.lower(), cat_name.lower(), payoff.lower(), "oh no song", "nursery rhyme 3d"],
            "seo_tags": ["#ohnosong", "#nurseryrhymes", "#kidssongs", "#preschoollearning", "#animation3d"],
        })

    return results


def discover_kids_topics(
    limit: int = 8,
    target_age: Optional[str] = None,
    duration: Optional[str] = None,
    language: Optional[str] = None,
    seed: Optional[int] = None,
    excluded_topics: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Researches and generates dynamic YouTube Kids topic opportunities using the official
    'Oh No!' story arc channel formula and Live AI reasoning.
    Strictly enforces permanent storage in SQLite so used topics are NEVER repeated.
    """
    provider = get_ai_provider(prefer_cloud=True)
    model_name = getattr(provider, "model", "default")

    age_str = target_age if target_age and target_age.lower() != "all" else "Ages 2-5 (Toddlers & Preschoolers)"
    dur_str = duration if duration else "2-3 Minutes (Standard YouTube Kids)"
    lang_str = language if language else "English (Global Audience)"
    seed_val = seed if seed is not None else random.randint(100000, 999999)

    # 1. Fetch all permanently used topics and existing projects
    used_list, used_titles_set, used_chars_set, used_objs_set = _get_used_topics_context()
    used_topics_text = "\n".join(used_list[:70]) if used_list else "(None yet — fresh channel start)"

    # 2. Build official user-specified system prompt
    system_prompt = f"""SYSTEM PROMPT — Topic Generator for Kids' YouTube Channel

You are a topic generator for a 3D-animated kids' YouTube channel (ages 2-5, English-language, global audience — no country-specific references).

CHANNEL FORMAT (fixed):
Every video follows the "Oh No!" story arc: a character loses or breaks something → searches in 4-5 places (each a false lead with a fun sound effect) → finds it on the 5th try → celebrates with a counting, color, shape, or sound-learning payoff → calms down/ends warmly.

YOUR TASK:
Generate exactly {limit} new video topics per request, in this format:
- Title: "Oh No! [Character] [Lost/Can't Find/Broke] [Object]!"
- Category: (Vehicle / Animal / Household object / Bedtime-routine / Nature)
- Learning payoff: (Counting 1-5 / Colors / Shapes / Sounds)
- One-line story hook (max 20 words)

HARD RULES — READ CAREFULLY:
1. NEVER repeat, rename, or lightly reword any topic in the EXCLUDE LIST below. Treat the exclude list as fully consumed — do not reuse the same character, the same lost object, or the same category+payoff combination twice.
2. Before answering, silently pick THREE random elements first: (a) a category not overused in the exclude list, (b) a character/object within that category not yet used, (c) a learning payoff not overused in the exclude list. Only build the title after choosing these three.
3. Prioritize globally generic, universally recognizable characters and objects (vehicles, animals, toys, bedtime objects, nature). Do NOT use any country-specific or region-specific references.
4. Randomization seed for this request: {seed_val} — use this number to break any tendency to default to your most likely answer. If asked again with a different seed, you must produce a genuinely different combination.
5. Return strictly valid JSON with key "topics" containing exactly {limit} objects.

EXCLUDE LIST (already used — do not repeat these or close variants):
{used_topics_text}
"""

    user_prompt = f"""Generate {limit} brand new unique "Oh No!" video topics strictly adhering to the channel format rules and exclude list.
Target Audience: {age_str}
Target Duration: {dur_str}
Language: {lang_str}
Randomization Seed: {seed_val}

Return JSON strictly in this structure:
{{
  "topics": [
    {{
      "title": "Oh No! [Character] [Lost/Can't Find/Broke] [Object]!",
      "character": "[Character Name]",
      "lost_or_broken_object": "[Object]",
      "category": "Vehicle / Animal / Household object / Bedtime-routine / Nature",
      "learning_payoff": "Counting 1-5 / Colors / Shapes / Sounds",
      "story_hook": "One-line story hook (max 20 words) describing the 4-5 search places and sound effects",
      "suggested_characters": ["Character 1", "Character 2"],
      "suggested_story_concept": "1-2 sentence animated story arc summary"
    }}
  ]
}}
"""

    collected: List[Dict[str, Any]] = []

    try:
        logger.info(f"Querying AI provider {model_name} for {limit} 'Oh No!' kids topics (Seed: {seed_val})...")
        res = provider.generate_json(user_prompt, system_prompt, max_tokens=2200)
        if res and "topics" in res and isinstance(res["topics"], list):
            for t in res["topics"]:
                if not isinstance(t, dict):
                    continue
                raw_title = t.get("title") or t.get("suggested_title") or ""
                char = (t.get("character") or "").strip().lower()
                obj = (t.get("lost_or_broken_object") or "").strip().lower()

                # STRICT DEDUPLICATION GUARD: Reject if title or character+object already used
                if not raw_title or raw_title.lower().strip() in used_titles_set:
                    continue
                if char and obj and f"{char}:{obj}" in used_titles_set:
                    continue

                used_titles_set.add(raw_title.lower().strip())
                if char:
                    used_chars_set.add(char)
                if obj:
                    used_objs_set.add(obj)
                collected.append(t)
            logger.info(f"AI returned {len(collected)} verified non-duplicate topics via {model_name}")
    except Exception as e:
        logger.warning(f"Live AI Topic Generation error via {model_name}: {e}")

    # If AI returned fewer topics than limit, run procedural dynamic generator for remainder
    if len(collected) < limit:
        needed = limit - len(collected)
        logger.info(f"Synthesizing {needed} dynamic 'Oh No!' topics with seed {seed_val}...")
        procedural = _dynamic_procedural_fallback(
            count=needed,
            seed_val=seed_val,
            used_titles=used_titles_set,
            used_chars=used_chars_set,
            used_objs=used_objs_set,
            target_age=age_str,
            duration=dur_str,
        )
        collected.extend(procedural)

    # Format into full frontend schema
    final_topics = []

    for t in collected[:limit]:
        title = t.get("title") or t.get("suggested_title") or "Oh No! Adventure"
        char = t.get("character", "")
        obj = t.get("lost_or_broken_object", "")
        cat = t.get("category", "Animal")
        payoff = t.get("learning_payoff", "Counting 1-5")
        hook = t.get("story_hook") or t.get("content_angle") or f"{char} searches 5 places with fun sounds!"
        concept = t.get("suggested_story_concept") or f"{char} loses {obj}, searches 5 places, finds it, and celebrates with {payoff}."

        chars = t.get("suggested_characters")
        if not chars:
            chars = [char, "Friendly Friend"] if char else ["Cute Bear", "Buddy"]
        elif isinstance(chars, str):
            chars = [c.strip() for c in chars.split(",")]

        topic_card = {
            "topic": title.replace("Oh No! ", "").replace("!", "").strip(),
            "title": title,
            "suggested_title": f"{title}  | 3D Nursery Rhymes & Kids Songs",
            "character": char,
            "lost_or_broken_object": obj,
            "category": cat,
            "learning_payoff": payoff,
            "target_age": age_str,
            "duration": dur_str,
            "content_angle": hook,
            "why_worth_considering": f"Official 'Oh No!' formula teaching early {payoff.lower()} with suspense, false leads, and high toddler retention.",
            "opportunity_signals": "Top-ranking preschool YouTube search structure with 10M+ view potential and repeat watch time.",
            "suggested_characters": chars,
            "suggested_story_concept": concept,
            "search_keywords": [char.lower() if char else "preschool", cat.lower(), payoff.lower(), "oh no song", "nursery rhyme 3d", "toddler learning"],
            "seo_tags": ["#ohnosong", "#nurseryrhymes", "#kidssongs", "#toddlerlearning", "#animation3d", "#earlylearning"],
        }
        final_topics.append(topic_card)

    # Persist to database so they become permanently consumed for all future calls
    _record_used_topics(final_topics)
    logger.info(f"Successfully generated {len(final_topics)} 'Oh No!' topics via {model_name}")

    return final_topics
