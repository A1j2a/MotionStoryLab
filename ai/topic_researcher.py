import json
import logging
from typing import Dict, Any, List
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.topics")

CURATED_TOPIC_POOL = [
    {
        "topic": "Toto the Little Train Meets Farm Animals",
        "suggested_title": "Toto the Choo-Choo Train & Farm Animals 🚂 | Toddler Learning Song",
        "category": "Vehicles & Animals",
        "target_age": "1–4 Years",
        "search_keywords": ["train song for kids", "choo choo train", "farm animal sounds", "toddler nursery rhymes", "train cartoon 3d"],
        "content_angle": "Combines high-interest vehicle movement with call-and-response farm animal sounds (moo, baa, oink) to build early vocabulary.",
        "why_worth_considering": "High evergreen search interest with strong toddler retention when combining trains and animals.",
        "opportunity_signals": "High search volume on YouTube Kids with above-average watch-time duration for repetitive rhythm songs.",
        "suggested_characters": ["Toto the Blue Engine", "Daisy the Cow", "Benny Duck", "Barnaby Bear"],
        "suggested_story_concept": "Toto rolls happily down the railway tracks, stopping at friendly meadow stations where funny animals hop on board for a musical ride.",
    },
    {
        "topic": "Twinkle Little Star and the Smiling Crescent Moon",
        "suggested_title": "Twinkle Twinkle Little Star ✨ Soothing 3D Bedtime Lullaby for Babies",
        "category": "Bedtime & Lullabies",
        "target_age": "0–3 Years",
        "search_keywords": ["twinkle twinkle little star", "bedtime lullaby for babies", "sleep music toddler", "night sky cartoon", "soothing baby songs"],
        "content_angle": "Ultra-calming bedtime tempo (75 BPM) with glowing celestial characters and soft twinkling star chime arrangements.",
        "why_worth_considering": "Bedtime content has the highest repeat-view multiplier on YouTube Kids, often playing on loop for 30+ minutes.",
        "opportunity_signals": "Consistent search demand across global timezones for bedtime routines and baby sleep aids.",
        "suggested_characters": ["Twinkle Star", "Smiling Moon", "Puffy Cloud", "Little Comet"],
        "suggested_story_concept": "Twinkle Star drifts through a cozy indigo sky, helping tired clouds tuck in the little planets before wishing all children sweet dreams.",
    },
    {
        "topic": "The Wheels on the Bright Yellow School Bus",
        "suggested_title": "Wheels on the Yellow School Bus 🚌 | Interactive Preschool Dance Song",
        "category": "Preschool Classics",
        "target_age": "2–5 Years",
        "search_keywords": ["wheels on the bus", "bus song for toddlers", "preschool action song", "cocomelon style bus", "interactive kids dance"],
        "content_angle": "Action-driven physical movements (spinning wheels, swishing wipers, beeping horns) encouraging toddler physical engagement.",
        "why_worth_considering": "The single most searched nursery rhyme format worldwide with universal familiarity.",
        "opportunity_signals": "Massive global search intent with high replay value when visual characters have distinctive personality quirks.",
        "suggested_characters": ["Buster the Bus", "Officer Panda", "Mimi the Kitten", "Pip the Puppy"],
        "suggested_story_concept": "Buster the yellow bus rolls through Rainbow Town picking up cute animal friends on their way to the grand playground festival.",
    },
    {
        "topic": "Five Little Ducks Went Swimming in the Rainbow River",
        "suggested_title": "Five Little Ducks Swimming! 🦆 Learn Numbers 1 to 5 | Counting Song",
        "category": "Numbers & Counting",
        "target_age": "1–4 Years",
        "search_keywords": ["five little ducks", "counting 1 to 5 for toddlers", "duck nursery rhyme", "math preschool song", "kids animal songs"],
        "content_angle": "Clear numerical countdown structure from 5 to 1 with emotional story resolution when all ducks return happily to Mother Duck.",
        "why_worth_considering": "Educational counting songs receive strong parental approval and classroom playlist inclusion.",
        "opportunity_signals": "Strong search volume for preschool numeracy and emotional reunion narratives.",
        "suggested_characters": ["Mother Duck", "Ducky One", "Ducky Two", "Ducky Three", "Ducky Four", "Ducky Five"],
        "suggested_story_concept": "Five playful ducklings explore over the colorful hills and lily ponds, discovering fun sights before Mother Duck calls them back home.",
    },
    {
        "topic": "The Dancing Yummy Fruits and Vegetables",
        "suggested_title": "Healthy Yummy Fruits Song 🍎🍌 | Fun Food Adventure for Toddlers",
        "category": "Healthy Habits & Food",
        "target_age": "2–5 Years",
        "search_keywords": ["fruit song for kids", "healthy food toddler", "dancing apple banana", "colors of fruits song", "vegetable rhyme preschool"],
        "content_angle": "Celebrates colors, textures, and tastes of wholesome fruits with catchy dance choreography.",
        "why_worth_considering": "Parents actively seek positive mealtime reinforcement videos to help picky eaters enjoy healthy food.",
        "opportunity_signals": "High co-viewing rates with parents looking for mealtime encouragement songs.",
        "suggested_characters": ["Happy Apple", "Sunny Banana", "Berry Strawberry", "Professor Broccoli"],
        "suggested_story_concept": "A cheerful fruit bowl turns into a lively kitchen stage where crunchy apples and sweet berries teach toddlers about healthy energy.",
    },
    {
        "topic": "Five Friendly Dinosaurs Having a Jungle Parade",
        "suggested_title": "Five Friendly Dinosaurs Stomp & Roar! 🦖 | Fun Dinosaur Dance Song",
        "category": "Fantasy & Dinosaurs",
        "target_age": "2–6 Years",
        "search_keywords": ["dinosaur song for kids", "dino dance toddler", "friendly t-rex song", "jurassic cartoon for preschoolers", "stomp and roar kids"],
        "content_angle": "Playful stomping beats and cheerful roars with cute rounded non-scary cartoon dinosaurs.",
        "why_worth_considering": "Dinosaur topics hold disproportionately high click-through rates among preschool boys and girls.",
        "opportunity_signals": "High search volume spike for friendly preschool dino content without scary visuals.",
        "suggested_characters": ["Rexy the Tiny T-Rex", "Tops the Triceratops", "Bronto the Gentle Giant", "Ptera the Flyer"],
        "suggested_story_concept": "Rexy and his prehistoric jungle pals organize a friendly stomp-and-dance parade across the sunflower plains.",
    },
    {
        "topic": "Brush Your Teeth Clean and Bright",
        "suggested_title": "Brush Brush Brush Your Teeth! 🪥 | 2-Minute Habit Song for Toddlers",
        "category": "Good Habits & Routines",
        "target_age": "1–5 Years",
        "search_keywords": ["brush your teeth song", "2 minute toothbrushing song", "toddler morning routine", "healthy habits for kids", "bathroom routine song"],
        "content_angle": "Timed exactly to 2 minutes of active brushing rhythm with bubble popping and sparkly teeth visual effects.",
        "why_worth_considering": "High daily routine usage where parents play the video every morning and evening.",
        "opportunity_signals": "Evergreen recurring daily sessions with extremely high retention during routine times.",
        "suggested_characters": ["Sparkle the Toothbrush", "Bubble Bear", "Shiny Tooth"],
        "suggested_story_concept": "Bubble Bear and Sparkle make morning bathroom routines exciting by dancing away sleepy sugar bugs with foamy bubbles.",
    },
    {
        "topic": "The Big Colorful Fire Truck to the Rescue",
        "suggested_title": "Fire Truck to the Rescue! 🚒 | Community Heroes Kids Song",
        "category": "Community Heroes & Vehicles",
        "target_age": "2–6 Years",
        "search_keywords": ["fire truck song kids", "rescue vehicles toddler", "emergency vehicles cartoon", "firefighter song preschool", "siren song"],
        "content_angle": "Heroic upbeat brass march celebrating teamwork, problem-solving, and helping friends in need.",
        "why_worth_considering": "Community vehicle videos consistently rank in the top 10% for preschool watch time.",
        "opportunity_signals": "Strong search demand for fire truck sirens, water splashing, and heroic rescue themes.",
        "suggested_characters": ["Flash the Fire Engine", "Chief Charlie Dog", "Kitty in the Tree"],
        "suggested_story_concept": "Flash hears the alarm and zooms through Town Square with flashing lights to help rescue a playful kitten stuck in a blooming cherry tree.",
    },
    {
        "topic": "Color Mixing Magic with Rainbow Paint Pots",
        "suggested_title": "Learn Colors with Magic Paint! 🎨 | Rainbow Mixing Preschool Song",
        "category": "Colors & Creativity",
        "target_age": "1–4 Years",
        "search_keywords": ["learn colors song", "color mixing toddler", "rainbow song for kids", "red yellow blue colors", "preschool color lesson"],
        "content_angle": "Visual color transformation (Red + Yellow = Orange, Blue + Yellow = Green) shown through bouncy paint splashes.",
        "why_worth_considering": "Fundamental early childhood learning milestone with high search intent from parents and teachers.",
        "opportunity_signals": "Consistent search interest year-round across international English-learning audiences.",
        "suggested_characters": ["Splatter the Paintbrush", "Ruby Red", "Sunny Yellow", "Ocean Blue"],
        "suggested_story_concept": "Splatter and his colorful paint friends jump into empty canvases, mixing their shades together to create a giant rainbow mural.",
    },
    {
        "topic": "Old MacDonald's Animal Talent Show",
        "suggested_title": "Old MacDonald Had a Farm! 🚜 Sing Along Farm Animals Cartoon",
        "category": "Preschool Classics",
        "target_age": "1–4 Years",
        "search_keywords": ["old macdonald had a farm", "farm animal sounds kids", "tractor song for toddlers", "sing along farm", "cocomelon farm rhyme"],
        "content_angle": "Fresh modern musical twist where farm animals take turns showing funny dance moves and instrument solos.",
        "why_worth_considering": "Top 3 all-time most recognized nursery rhyme format globally.",
        "opportunity_signals": "High search volume with long session watch time when rendered with vibrant 3D cartoon visuals.",
        "suggested_characters": ["Farmer Mac", "Daisy Cow", "Barnaby Pig", "Clucky Hen", "Baa Baa Sheep"],
        "suggested_story_concept": "Farmer Mac drives his bright green tractor out to the barnyard where each animal friend steps up to sing their signature sound.",
    },
    {
        "topic": "Clean Up, Clean Up, Put Your Toys Away",
        "suggested_title": "The Clean Up Song! 🧸 | Fun 2-Minute Tidy Up Time for Kids",
        "category": "Good Habits & Routines",
        "target_age": "1–5 Years",
        "search_keywords": ["clean up song", "tidy up song for kids", "put toys away song", "preschool transition song", "classroom clean up"],
        "content_angle": "Bouncy marching tempo that turns cleaning the playroom into a fun cooperative game of sorting blocks and teddy bears.",
        "why_worth_considering": "Essential tool used daily by hundreds of thousands of daycare centers, preschools, and parents.",
        "opportunity_signals": "High frequency of daily recurring plays during playroom cleanup time.",
        "suggested_characters": ["Teddy Barnaby", "Boxy Toy Chest", "Speedy Toy Car"],
        "suggested_story_concept": "When playtime is done, the toys march happily back to their colorful cozy shelves before settling in for afternoon storytime.",
    },
    {
        "topic": "Bouncing Ball and the Jungle Hop",
        "suggested_title": "Hop, Jump & Dance! 🦘 | Active Movement Song for Toddlers",
        "category": "Dance & Movement",
        "target_age": "2–5 Years",
        "search_keywords": ["jump and hop song", "freeze dance for toddlers", "active kids workout", "preschool dance song", "indoor energy burning song"],
        "content_angle": "High-energy physical interactive prompts (Jump 3 times, Hop like a bunny, Freeze!) for indoor exercise.",
        "why_worth_considering": "High engagement metric as children physically jump and dance along with on-screen characters.",
        "opportunity_signals": "Strong search volume during morning energetic play sessions and rainy day indoor play.",
        "suggested_characters": ["Bouncy Kangaroo", "Freddy Frog", "Sunny Bunny"],
        "suggested_story_concept": "Bouncy Kangaroo leads all the jungle animals in a joyful hop-and-freeze dance competition across giant mossy stepping stones.",
    },
]


def discover_kids_topics(limit: int = 12) -> List[Dict[str, Any]]:
    """
    Researches and generates 10–15 structured kids video topic opportunity cards.
    Queries the configured AIProvider (OmniRoute / Ollama / Claude) and falls back to rich curated pool.
    """
    provider = get_ai_provider()
    
    prompt = f"""Generate {limit} fresh, high-performing YouTube Kids 3D animated nursery rhyme and educational song topic opportunities.
Target Audience: Toddlers & Preschoolers (Ages 1-5).
Style: Cocomelon, Super Simple Songs, Badanamu.
Return a valid JSON object with a "topics" list of {limit} objects. Each object MUST contain:
- "topic": Clear theme idea
- "suggested_title": High-CTR catchy YouTube title with emojis
- "category": e.g. "Vehicles & Animals", "Numbers & Counting", "Good Habits", "Bedtime Lullabies"
- "target_age": e.g. "1–4 Years"
- "search_keywords": list of 5 search terms
- "content_angle": what makes this video engaging
- "why_worth_considering": audience appeal rationale (do NOT promise viral)
- "opportunity_signals": search intent & relevance indicators
- "suggested_characters": list of 3-4 character names
- "suggested_story_concept": 1-2 sentence storyline
"""
    system_prompt = "You are a top YouTube Kids preschool algorithm and content strategy researcher. Never make claims about guaranteed virality. Output valid JSON only."

    try:
        res = provider.generate_json(prompt, system_prompt)
        if res and "topics" in res and isinstance(res["topics"], list) and len(res["topics"]) >= 5:
            logger.info(f"Generated {len(res['topics'])} topics via {provider.__class__.__name__}")
            return res["topics"][:limit]
    except Exception as e:
        logger.warning(f"AI topic research failed, using curated pool: {e}")

    return CURATED_TOPIC_POOL[:limit]
