import json
import logging
from typing import Dict, Any, List, Optional
from ai.providers import get_ai_provider

logger = logging.getLogger("studio.ai.topics")

# High-engagement categorized topic opportunity templates tailored for kids preschool content
TOPIC_POOLS = {
    "english": [
        {
            "topic": "The Animal Bus Ride",
            "suggested_title": "The Animal Bus Ride 🚌🐱🐶 | Kids Sing-Along Nursery Rhyme",
            "category": "Vehicles & Animals",
            "content_angle": "Bella the Blue Bus picks up singing animal friends across Sunny Valley who each perform their signature rhyming verse.",
            "why_worth_considering": "The combination of beloved animals and friendly vehicles consistently ranks among the highest-performing preschool content pillars.",
            "opportunity_signals": "Searches for 'animal bus rhyme' and 'toddler vehicle songs' maintain year-round top-tier watch time and high repeat loop value.",
            "suggested_characters": ["Bella the Blue Bus", "Leo the Lion", "Mia the Mouse", "Barnaby Bear"],
            "suggested_story_concept": "Bella the Bus rolls through rolling pastel hills, picking up adorable animal friends who tap their paws and sing along to the horn toot.",
        },
        {
            "topic": "Count the Stars",
            "suggested_title": "✨ Count the Stars! | Bedtime Counting Song for Kids 🎶",
            "category": "Numbers & Counting",
            "content_angle": "Gentle lullaby counting from 1 to 10 with glowing friendly stars lighting up the twilight night sky.",
            "why_worth_considering": "Bedtime number songs merge two high-demand preschool categories: soothing bedtime routines and early numeracy fundamentals.",
            "opportunity_signals": "'Counting songs for toddlers' and 'bedtime lullaby' searches peak during evening bedtime routines with exceptional completion rates.",
            "suggested_characters": ["Orby the Owl", "Twinkle the Star", "Numby the Number Bunny"],
            "suggested_story_concept": "Orby the Owl flies across the enchanted night sky counting stars that light up in sequence, helping little ones drift off to dreamland.",
        },
        {
            "topic": "Brush Brush Dance",
            "suggested_title": "🪥 Brush Brush Dance! | Fun Teeth Brushing Song for Kids 🎵",
            "category": "Good Habits",
            "content_angle": "Timed 2-minute tooth-brushing routine set to a cheerful bubbly beat that turns morning and night routines into a fun disco dance.",
            "why_worth_considering": "Parents actively seek engaging 2-minute brushing timers to solve daily toddler bathroom struggles, resulting in daily recurring plays.",
            "opportunity_signals": "'Teeth brushing song for toddlers' searches spike twice daily with nearly 100% video completion rates.",
            "suggested_characters": ["Sparkle the Toothpaste", "Brushy the Toothbrush", "Finn the Foamy Bear"],
            "suggested_story_concept": "Sparkle and Brushy throw a bubbly dance party inside a giant colorful bathroom, showing kids how to brush top, bottom, and round and round.",
        },
        {
            "topic": "The Rainbow Color Train",
            "suggested_title": "Choo Choo Color Train! 🚂🎨 | Learn Rainbow Colors with Trains",
            "category": "Colors & Shapes",
            "content_angle": "A playful choo-choo train delivers colorful toy cars with vibrant paint splashes and cheerful rhythmic chugging sounds.",
            "why_worth_considering": "Train sound effects combined with primary color discovery create an irresistible audiovisual feedback loop for toddlers.",
            "opportunity_signals": "'Color train for kids' is one of the top preschool discovery search terms worldwide.",
            "suggested_characters": ["Toto the Color Train", "Pip the Paintbrush", "Daisy the Duck"],
            "suggested_story_concept": "Toto chugs into Color Station loading red apples, blue balloons, yellow stars, and green frogs into each matching cargo wagon.",
        },
        {
            "topic": "Friendly Dino Stomp",
            "suggested_title": "Roar Like a Friendly Dino! 🦖🌴 | Toddler Stomp & Dance Exercise",
            "category": "Adventure & Science",
            "content_angle": "High-energy physical interactive movement song encouraging toddlers to stomp like a brontosaurus and flap like a pterodactyl.",
            "why_worth_considering": "Active movement and dinosaur themes drive exceptionally high viewer engagement and physical participation from children.",
            "opportunity_signals": "'Dinosaur dance for kids' experiences massive weekend search volumes during indoor playtime.",
            "suggested_characters": ["Dino Dan", "Tara the Pterodactyl", "Stompy the Stegosaurus"],
            "suggested_story_concept": "Dino Dan leads all jungle friends on a bouncy dinosaur parade through a prehistoric playground of giant pastel ferns.",
        },
        {
            "topic": "Bath Time Bubble Splash",
            "suggested_title": "Bath Time Bubble Party! 🛁🫧 | Splish Splash Fun Hygiene Song",
            "category": "Good Habits",
            "content_angle": "Splashing water rhythm and floating bubble pops that help toddlers enjoy evening bath routines without fuss.",
            "why_worth_considering": "Bath anxiety is a universal parent pain point; fun musical cues transform bath time into positive play.",
            "opportunity_signals": "High search volume among parents of 1-3 year olds looking for gentle water acclimation videos.",
            "suggested_characters": ["Bubbles the Rubber Ducky", "Splishy the Whale", "Pip the Penguin"],
            "suggested_story_concept": "A warm bubbly tub transforms into a playful ocean voyage where floating rubber toys sing and pop rainbow bubbles.",
        },
        {
            "topic": "Rocket Ship to the Moon",
            "suggested_title": "Zoom to the Moon! 🚀🌙 | Solar System Space Song for Toddlers",
            "category": "Adventure & Science",
            "content_angle": "Countdown blastoff from 5 to 1 followed by a floating cosmic tour visiting glowing pastel planets.",
            "why_worth_considering": "Space exploration introduces gentle STEM curiosity while capitalizing on toddler fascination with rockets.",
            "opportunity_signals": "'Space songs for preschool' has high evergreen educational search volume in schools and daycares.",
            "suggested_characters": ["Captain Cosmo Bear", "Nova the Rocket", "Luna the Moon Bunny"],
            "suggested_story_concept": "Captain Cosmo straps into his shiny rocket, counts down with stars, and floats weightlessly past friendly smiling planets.",
        },
        {
            "topic": "Yummy Rainbow Fruit Bowl",
            "suggested_title": "The Yummy Fruit Salad Song! 🍎🍌🍓 | Healthy Eating Song for Kids",
            "category": "Good Habits",
            "content_angle": "Dancing fruits hop into a big glass bowl singing about their bright colors, sweet vitamins, and crunchy textures.",
            "why_worth_considering": "Parents actively play healthy eating songs during snack time to encourage trying new fruits and vegetables.",
            "opportunity_signals": "Strong shares in parenting and preschool teacher communities during nutrition lesson weeks.",
            "suggested_characters": ["Apple Annie", "Berry Benny", "Sunny Banana"],
            "suggested_story_concept": "Cheerful singing fruits do a rhythmic tap dance, jumping into a crystal bowl to create a delicious colorful rainbow treat.",
        },
        {
            "topic": "Five Little Ducks Ocean Adventure",
            "suggested_title": "Five Little Ducks Went Swimming! 🦆🌊 | 3D Nursery Rhyme Classic",
            "category": "Numbers & Counting",
            "content_angle": "Modern 3D animated visual treatment of the timeless subtraction song with playful water slide animations.",
            "why_worth_considering": "Consistently recognized as one of the top 5 nursery rhymes of all time with multi-generational familiarity.",
            "opportunity_signals": "Billions of cumulative global views across platforms with evergreen monthly algorithmic discovery.",
            "suggested_characters": ["Mother Duck", "Ducky Dan", "Ducky Dot", "Ducky Pip", "Ducky Sam"],
            "suggested_story_concept": "Five fluffy yellow ducklings slide down leafy water slides into a sparkling lake, returning with big joyful quacks to Mother Duck.",
        },
        {
            "topic": "Fire Truck to the Rescue",
            "suggested_title": "Fire Truck to the Rescue! 🚒🚨 | Brave Community Helpers Song",
            "category": "Vehicles & Animals",
            "content_angle": "Upbeat brass march celebrating teamwork, problem-solving, and community helpers with flashing lights.",
            "why_worth_considering": "Emergency vehicles consistently achieve the highest thumbnail click-through rates among preschool boys and girls.",
            "opportunity_signals": "Massive search volume for sirens, rescue trucks, and friendly firefighter heroes.",
            "suggested_characters": ["Flash the Fire Truck", "Chief Charlie Dog", "Kitty in the Tree"],
            "suggested_story_concept": "Flash zooms through Sunnyville with cheerful sirens to safely rescue a playful kitten stuck in a blooming cherry tree.",
        },
        {
            "topic": "The 2-Minute Clean Up Song",
            "suggested_title": "Tidy Up, Play Time's Done! 🧸🧺 | Fun Clean Up Song for Kids",
            "category": "Good Habits",
            "content_angle": "Bouncy marching rhythm turning toy clean-up into an interactive game of sorting blocks, cars, and teddy bears.",
            "why_worth_considering": "Essential transition tool used daily by hundreds of thousands of daycare centers, preschools, and parents.",
            "opportunity_signals": "High frequency of daily recurring plays during playroom cleanup time.",
            "suggested_characters": ["Teddy Barnaby", "Boxy Toy Chest", "Speedy Toy Car"],
            "suggested_story_concept": "When the musical bell rings, toy blocks and dolls march happily back to their colorful shelves before afternoon snack time.",
        },
        {
            "topic": "Sleepy Little Koala Lullaby",
            "suggested_title": "Sleepy Little Koala Lullaby 🐨⭐ | Gentle Bedtime Calming Music",
            "category": "Bedtime Lullabies",
            "content_angle": "Soft acoustic lullaby with gentle white noise chimes designed for soothing cranky toddlers to sleep.",
            "why_worth_considering": "Bedtime content has the highest watch time duration per session on YouTube Kids.",
            "opportunity_signals": "'Toddler sleep music' and 'calming lullaby' generate continuous high-retention overnight watch hours.",
            "suggested_characters": ["Koko the Koala", "Mother Koala", "Sleepy Moon"],
            "suggested_story_concept": "Koko snuggles into a cozy eucalyptus tree hammock as twinkling fireflies light the way to peaceful dreams.",
        },
    ],
    "hindi": [
        {
            "topic": "चंदा मामा दूर के",
            "suggested_title": "चंदा मामा दूर के! 🌙✨ | Chanda Mama Pyare 3D Hindi Rhyme",
            "category": "Bedtime Lullabies",
            "content_angle": "Traditional Hindi bedtime classic with modern 3D magical visuals and soothing soothing melody.",
            "why_worth_considering": "The #1 most requested Hindi nursery rhyme across Indian and diaspora families worldwide.",
            "opportunity_signals": "Over 500M+ views across top Indian kids channels with high repeat evening viewership.",
            "suggested_characters": ["Chanda Mama", "Munna", "Gudiya"],
            "suggested_story_concept": "Munna and Gudiya eat sweet kheer on the terrace as smiling Chanda Mama dances among sparkling stars.",
        },
        {
            "topic": "मछली जल की रानी है",
            "suggested_title": "मछली जल की रानी है! 🐟🌊 | Machli Jal Ki Rani 3D Nursery Rhyme",
            "category": "Vehicles & Animals",
            "content_angle": "Colorful underwater adventure with bouncing fish friends swimming through coral kingdoms.",
            "why_worth_considering": "Universal cultural familiarity taught in every Indian preschool and kindergarten.",
            "opportunity_signals": "High search volume in India, UAE, US, and UK among Hindi-speaking households.",
            "suggested_characters": ["Rani the Fish", "Chhotu the Crab", "Tara the Starfish"],
            "suggested_story_concept": "Rani the golden fish performs joyful water flips with coral reef friends in crystal blue waters.",
        },
        {
            "topic": "तितली उड़ी बस पे चढ़ी",
            "suggested_title": "तितली उड़ी बस पे चढ़ी! 🦋🚌 | Titli Udi Fun Hindi Rhyme for Kids",
            "category": "Vehicles & Animals",
            "content_angle": "Lively rhyming story of a playful butterfly flying onto a red bus and making friends with the driver.",
            "why_worth_considering": "High humor and rhythmic rhyming cadence that toddlers love reciting aloud.",
            "opportunity_signals": "Strong search volume for Hindi animal rhymes with high preschool audience retention.",
            "suggested_characters": ["Titli the Butterfly", "Bholu the Driver", "Munni"],
            "suggested_story_concept": "Titli flies through flower gardens, hops onto the village bus, and gets rewarded with sweet mangoes.",
        },
        {
            "topic": "दांत साफ़ करो रोज सुबह",
            "suggested_title": "दांत साफ़ करो रोज सुबह! 🪥🦷 | Brush Your Teeth Hindi Kids Song",
            "category": "Good Habits",
            "content_angle": "Fun 2-minute tooth brushing routine in Hindi teaching morning hygiene with bubbly animation.",
            "why_worth_considering": "Parents actively look for Hindi habit-building songs for toddlers.",
            "opportunity_signals": "Rising demand for vernacular good-habit rhymes in Tier 1 and Tier 2 cities.",
            "suggested_characters": ["Chhotu", "Brushy Bhai", "Sparkle Didi"],
            "suggested_story_concept": "Chhotu dances with Brushy Bhai, fighting off naughty germ monsters with foamy mint bubbles.",
        },
        {
            "topic": "हाथी राजा कहाँ चले",
            "suggested_title": "हाथी राजा कहाँ चले! 🐘👑 | Hathi Raja Hindi Rhymes & Dance Song",
            "category": "Vehicles & Animals",
            "content_angle": "Grand friendly elephant swinging his trunk through the jungle bazaar to eat sweet puris.",
            "why_worth_considering": "Evergreen character recognition and cheerful elephant dance movements for toddlers.",
            "opportunity_signals": "Top 3 highest-searched vernacular animal songs in India.",
            "suggested_characters": ["Hathi Raja", "Mintu Bear", "Bholu Monkey"],
            "suggested_story_concept": "Hathi Raja proudly walks into the jungle party with his royal crown, enjoying sugarcane and sweet laddoos.",
        },
        {
            "topic": "गाड़ी आई छुक छुक छुक",
            "suggested_title": "गाड़ी आई छुक छुक छुक! 🚂💨 | Rail Gadi Hindi Train Song",
            "category": "Vehicles & Animals",
            "content_angle": "Rhythmic train sounds and cheerful animal passengers boarding across stations in India.",
            "why_worth_considering": "Train rhymes are universally loved by toddlers who enjoy imitating choo-choo sounds.",
            "opportunity_signals": "Massive replay value as toddlers dance in train formation at preschools.",
            "suggested_characters": ["Chhotu Driver", "Sheru Lion", "Tiku Parrot"],
            "suggested_story_concept": "A bright green steam train chugs past mango orchards, picking up animal friends singing chuk chuk chuk.",
        },
        {
            "topic": "एक दो तीन चार सितारे",
            "suggested_title": "एक दो तीन चार सितारे! ⭐🔢 | Hindi Counting Song 1 to 10 for Toddlers",
            "category": "Numbers & Counting",
            "content_angle": "Counting from 1 to 10 in Hindi with glowing balloons, colorful kites, and animated animals.",
            "why_worth_considering": "Fundamental early learning milestone for Hindi bilingual education.",
            "opportunity_signals": "High search interest from parents teaching counting in mother tongue.",
            "suggested_characters": ["Ginti Master", "Chhotu", "Tara"],
            "suggested_story_concept": "Kids count smiling floating balloons in the sky from 1 to 10, clapping on every number beat.",
        },
        {
            "topic": "बंदर मामा पहन पजामा",
            "suggested_title": "बंदर मामा पहन पजामा! 🐒🩳 | Bandar Mama Funny Hindi Kids Cartoon",
            "category": "Social-Emotional",
            "content_angle": "Hilarious comical rhyme of a mischievous monkey dressing up in pajamas to attend a wedding feast.",
            "why_worth_considering": "Slapstick humor and catchy rhythm guarantee giggles and repeat plays.",
            "opportunity_signals": "Immense evergreen popularity across YouTube Kids India.",
            "suggested_characters": ["Bandar Mama", "Halwai Bhai", "Dulha Raja"],
            "suggested_story_concept": "Bandar Mama puts on bright red pajamas, burns his tongue on hot rasgullas, and jumps into a cool pond.",
        },
    ],
    "spanish": [
        {
            "topic": "El Autobús de los Animales",
            "suggested_title": "¡El Autobús de los Animales! 🚌🐱🐶 | Canciones Infantiles para Niños",
            "category": "Vehicles & Animals",
            "content_angle": "Ruta musical interactiva en autobús donde los animales suben cantando sus divertidos sonidos.",
            "why_worth_considering": "Los vehículos y animales son los temas más buscados en América Latina y España.",
            "opportunity_signals": "Millones de búsquedas mensuales para canciones de ruedas del autobús en español.",
            "suggested_characters": ["Tito el Autobús", "Gatito Mia", "Perrito Toby"],
            "suggested_story_concept": "Tito viaja por colinas de colores recogiendo amigos que cantan y tocan la bocina.",
        },
        {
            "topic": "A Lavarse los Dientes",
            "suggested_title": "¡A Lavarse los Dientes! 🪥🎵 | Canción de Buenos Hábitos Infantiles",
            "category": "Good Habits",
            "content_angle": "Rutina divertida de 2 minutos para que los niños se cepillen con ritmo y burbujas.",
            "why_worth_considering": "Solución musical para la rutina diaria de higiene de los padres.",
            "opportunity_signals": "Búsquedas recurrentes cada mañana y noche en hogares hispanohablantes.",
            "suggested_characters": ["Cepillín", "Pasta Brillante", "Osito Pompas"],
            "suggested_story_concept": "Cepillín hace una fiesta de espuma en el baño enseñando a limpiar arriba, abajo y en círculos.",
        },
        {
            "topic": "Cinco Patitos",
            "suggested_title": "¡Cinco Patitos Nadando! 🦆🌊 | Rimas y Números para Bebés",
            "category": "Numbers & Counting",
            "content_angle": "Clásico infantil sobre números y resta con animaciones acuáticas llenas de ternura.",
            "why_worth_considering": "Reconocimiento universal en guarderías y colegios de todo el mundo hispano.",
            "opportunity_signals": "Búsquedas continuas todo el año con excelente retención de audiencia.",
            "suggested_characters": ["Mamá Pata", "Patito Juan", "Patito Pío"],
            "suggested_story_concept": "Cinco patitos traviesos nadan por la laguna hasta que regresan todos felices con Mamá Pata.",
        },
        {
            "topic": "El Tren de los Colores",
            "suggested_title": "¡El Tren de los Colores! 🚂🎨 | Aprende Colores Cantando en 3D",
            "category": "Colors & Shapes",
            "content_angle": "Tren sonriente que transporta vagones con pintura mágica y juguetes de cada color.",
            "why_worth_considering": "Hito fundamental de aprendizaje temprano en preescolar.",
            "opportunity_signals": "Alto volumen de búsqueda en España, México, Colombia y EE. UU.",
            "suggested_characters": ["El Tren Choo-Choo", "Pincelito", "Ranita Verde"],
            "suggested_story_concept": "El tren llega a la estación dejando globos rojos, patos amarillos y ranitas verdes.",
        },
    ]
}


def _get_curated_topics(
    limit: int = 8,
    target_age: Optional[str] = None,
    duration: Optional[str] = None,
    language: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Returns curated topic opportunities strictly tailored to age, duration, and language filters."""
    lang_key = "english"
    if language:
        l_lower = language.lower()
        if "hindi" in l_lower:
            lang_key = "hindi"
        elif "spanish" in l_lower:
            lang_key = "spanish"

    pool = list(TOPIC_POOLS.get(lang_key, TOPIC_POOLS["english"]))
    
    # If more items needed than in pool, wrap around or supplement from english pool
    while len(pool) < limit:
        for item in TOPIC_POOLS["english"]:
            if item not in pool:
                pool.append(item)
            if len(pool) >= limit:
                break
        if len(pool) < limit:
            break

    age_display = target_age if target_age and target_age.lower() != "all" else "2–5 Years"
    dur_display = duration if duration else "2–3 Minutes"

    results = []
    for item in pool[:limit]:
        c = dict(item)
        c["target_age"] = age_display
        c["duration"] = dur_display
        if "search_keywords" not in c:
            c["search_keywords"] = [c["topic"].lower(), "preschool song", "nursery rhyme 3d", "toddler video"]
        results.append(c)

    return results


def discover_kids_topics(
    limit: int = 8,
    target_age: Optional[str] = None,
    duration: Optional[str] = None,
    language: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Researches and generates dynamic YouTube Kids topic opportunities.
    Guarantees returning EXACTLY `limit` candidates matching age, duration & language.
    """
    provider = get_ai_provider()
    model_name = getattr(provider, "model", "default")

    age_str = target_age if target_age and target_age.lower() != "all" else "Toddlers & Preschoolers (Ages 1-5)"
    dur_str = duration if duration else "2-3 Minutes (Standard YouTube Kids)"
    lang_str = language if language else "English (US/UK)"

    lang_note = ""
    if "hindi" in lang_str.lower():
        lang_note = "LANGUAGE REQUIREMENT: Generate authentic Hindi & Hinglish preschool themes (like Chanda Mama, Titli Udi, Machli Jal Ki Rani, Gadi / Animal rhymes) with Hindi/Hinglish titles with friendly emojis."
    elif "spanish" in lang_str.lower():
        lang_note = "LANGUAGE REQUIREMENT: Generate authentic Spanish nursery rhymes (canciones infantiles) with Spanish titles with friendly emojis."
    elif "bilingual" in lang_str.lower():
        lang_note = "LANGUAGE REQUIREMENT: Generate bilingual English + Hindi / Spanish nursery rhyme themes designed for early multilingual learning."

    prompt = f"""Generate {limit} brand new, unique, high-performing YouTube Kids 3D animated nursery rhyme and preschool educational song topic opportunity cards.
Target Audience: {age_str}
Song Duration: {dur_str}
Target Language / Audience: {lang_str}
{lang_note}
STRICT COPYRIGHT & ORIGINALITY POLICY:
1. Every single topic, character, title, and story concept MUST be 100% original, copyright-free, and brand new.
2. NEVER use or reference any copyrighted characters, franchises, or brands (NO Cocomelon, Disney, Pixar, Marvel, Peppa Pig, Baby Shark, Pinkfong, Paw Patrol, Super Simple Songs, ChuChu TV, etc.).
3. Characters must be cute, original preschool characters (e.g. original animal buddies, friendly vehicles, celestial figures, or children).
4. Concepts must be fresh educational, musical, or good-habit learning songs.

Return ONLY a valid JSON object with a "topics" array containing exactly {limit} original, copyright-free topic objects.
Each topic object MUST contain:
- "topic": Short punchy theme name
- "suggested_title": High-CTR engaging YouTube title with friendly emojis
- "category": Choose from ("Vehicles & Animals", "Numbers & Counting", "Good Habits", "Bedtime Lullabies", "Colors & Shapes", "Social-Emotional", "Adventure & Science")
- "target_age": "{age_str}"
- "search_keywords": list of 5 high-intent preschool search keywords
- "content_angle": 1 sentence explaining the musical & visual engagement hook
- "why_worth_considering": 1 sentence audience & parental appeal rationale
- "opportunity_signals": 1 sentence search trend & repetition value indicator
- "suggested_characters": list of 3-4 cute character names
- "suggested_story_concept": 1-2 sentence animated storyboard concept
"""
    system_prompt = "You are a world-class preschool content strategist and original children songwriter. All generated concepts, characters, and titles MUST be 100% original, copyright-free, and brand new. Output strictly valid JSON with no conversational text."

    ai_topics: List[Dict[str, Any]] = []
    try:
        res = provider.generate_json(prompt, system_prompt, max_tokens=1800)
        if res and "topics" in res and isinstance(res["topics"], list):
            ai_topics = res["topics"]
            logger.info(f"AI returned {len(ai_topics)} topics via {model_name}")
    except Exception as e:
        logger.warning(f"AI Topic Generation call failed for {model_name}: {e}. Employing curated pool augmentation.")

    # If AI returned topics, use them
    final_topics = [t for t in ai_topics if isinstance(t, dict) and t.get("suggested_title")]
    for t in final_topics:
        t["duration"] = dur_str

    # If AI returned fewer topics than requested limit, augment with rich curated templates
    if len(final_topics) < limit:
        needed = limit - len(final_topics)
        existing_titles = {t.get("suggested_title", "").lower() for t in final_topics}
        curated_candidates = _get_curated_topics(limit=limit * 2, target_age=target_age, duration=duration, language=language)
        
        for cand in curated_candidates:
            if cand.get("suggested_title", "").lower() not in existing_titles:
                final_topics.append(cand)
                existing_titles.add(cand.get("suggested_title", "").lower())
            if len(final_topics) >= limit:
                break

    return final_topics[:limit]
