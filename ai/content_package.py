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

    system_prompt = f"You are an elite preschool children songwriter and animation director. Output 100% original, copyright-free preschool content scaled to last {target_dur:.1f} minutes. Output strictly valid JSON."

    try:
        data = provider.generate_json(prompt, system_prompt, max_tokens=2200)
        if data and "lyrics_full" in data and "characters" in data and isinstance(data["characters"], list):
            logger.info(f"Generated complete content package via {provider.__class__.__name__} for topic: {clean_topic} ({target_dur:.1f}m)")
            data["approved_lyrics"] = data["lyrics_full"]
            return data
    except Exception as e:
        logger.warning(f"AI content package generation failed, using procedural duration builder: {e}")

    return build_fallback_content_package(clean_topic, target_age, duration_minutes=target_dur)


def build_fallback_content_package(topic: str, target_age: str = "1–4 Years", duration_minutes: float = 2.0) -> Dict[str, Any]:
    """Guaranteed topic-matched, duration-scaled, copyright-clean content package engine."""
    clean_topic = topic.strip()
    topic_lower = clean_topic.lower()
    word_list = re.findall(r"\b\w+\b", topic_lower)
    words = set(word_list)
    target_dur = max(0.5, float(duration_minutes or 2.0))

    def has_kw(*keys):
        return any(k in topic_lower or k in words for k in keys)

    is_brush = has_kw("brush", "teeth", "tooth", "dental", "toothbrush", "toothpaste", "rinse", "hygiene", "dentist")
    is_bus = has_kw("bus", "wheels on", "school bus", "van")
    is_star = has_kw("star", "stars", "twinkle", "moon", "night", "lullaby")
    is_farm = has_kw("farm", "macdonald", "cow", "duck", "sheep", "pig", "barn", "tractor")
    is_fruit = has_kw("fruit", "fruits", "apple", "banana", "berry", "salad", "vegetable")
    is_dino = has_kw("dino", "dinosaur", "rex", "stomp", "jurassic")
    is_train = has_kw("train", "choo", "chugga", "rail", "railway", "locomotive")
    is_bath = has_kw("bath", "bubble", "bubbles", "splash", "soap", "tub", "splish")
    is_count = has_kw("count", "counting", "number", "numbers", "math", "1 to 10")
    is_color = has_kw("color", "colors", "rainbow", "paint")
    is_clean = has_kw("clean", "tidy", "toys", "cleanup")
    is_animal = has_kw("animal", "animals", "lion", "monkey", "tiger", "elephant", "zoo", "jungle")

    # Hindi specific
    is_chanda = has_kw("chanda", "mama", "chandamama")
    is_machli = has_kw("machli", "jal", "fish", "rani")
    is_titli = has_kw("titli", "butterfly")

    if is_brush:
        char_id = "brushy_bear"
        char_name = "Brushy Bear & Sparkle"
        species = "animal"
        title = "Brush Brush Dance! 🪥🦷 | Fun Teeth Brushing Song for Kids"
        env_name = "Sparkling Bubble Bathroom"
        v1_lines = [
            "Up and down, brush your teeth, brushing clean and bright,",
            "Morning time is here to stay, sparkling in the light!",
            "Take your little toothbrush now, squeeze a bubble dot,",
            "Brush every single happy tooth, front and top and spot!",
        ]
        ch_lines = [
            "Brush brush dance, brush brush dance, round and round we go,",
            "Singing our happy brushing song with a healthy glow!",
            "Two whole minutes, bubbly fun, smile so big and wide,",
            "Dancing with our toothbrush friends, happy on the slide!",
        ]
        v2_lines = [
            "Brush the teeth in the back, brush the teeth in front,",
            "Chasing all the sugar bugs on our morning hunt!",
            "Spit and rinse, splash splash splash, look at that bright grin,",
            "Every little boy and girl, ready to begin!",
        ]
        bridge_lines = [
            "Front teeth, back teeth, brush them with a smile,",
            "Sparkling so shiny, visible for a mile!",
            "Bubbles on the left, bubbles on the right,",
            "Dancing to the brushing rhythm, happy and bright!",
        ]
        v3_lines = [
            "Tickle tickle little tongue, rinse with water cool,",
            "Clean teeth every day is our favorite golden rule!",
            "Give a great big toddler grin into the mirror glass,",
            "We are the cleanest, happiest champions in the class!",
        ]
        outro_lines = [
            "Sparkly clean, shiny white, proud of what you have done,",
            "Teeth brushing every single day is so much healthy fun!",
            "Wave goodbye to Brushy Bear, keep on smiling bright,",
            "See you again for brush time when we say goodnight!",
        ]
        char_app = "Cute fluffy 3D toddler bear with rosy cheeks holding a friendly cartoon toothbrush with soft pastel foam bubbles."
        char_clothing = "Playful polka-dot morning pajamas and cozy slippers"
        char_anims = ["brush", "dance", "rinse", "smile", "bounce"]

    elif is_bus:
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
        bridge_lines = [
            "Gas pedal goes zoom, zoom, zoom down the sunny street,",
            "Radio plays a cheerful song with a bouncy toddler beat!",
            "Traffic light turns green and bright, Buster rolls along,",
            "All our little travel friends are singing with the song!",
        ]
        v3_lines = [
            "The steering wheel turns left and right, around the corner bend,",
            "Waving hello to everyone, each neighbor and each friend!",
            "Click click goes the seatbelt buckle, safe and happy ride,",
            "Looking at the pretty trees and flowers on each side!",
        ]
        outro_lines = [
            "Now we are at the playground, what a lovely ride,",
            "Everyone hop off and play on the giant slide!",
            "Thank you Buster Yellow Bus, wave goodbye with cheer,",
            "We will see you tomorrow for another sunny year!",
        ]
        char_app = "Cheerful yellow 3D animated school bus with big smiling cartoon eyes and friendly horn."
        char_clothing = "Bright yellow coat with red and blue hubcaps"
        char_anims = ["drive", "honk", "bounce", "swish"]

    elif is_star:
        char_id = "twinkle_star"
        char_name = "Twinkle Star"
        species = "celestial"
        title = "Twinkle Twinkle Little Star ✨ | Soothing 3D Bedtime Lullaby"
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
        bridge_lines = [
            "Shooting star zooms across, leaving trails of light,",
            "Whispering a lullaby through the velvet night!",
            "Teddy bear and puppy dog are tucked in cozy tight,",
            "Dreaming happy golden dreams until the morning bright!",
        ]
        v3_lines = [
            "Silver clouds are floating by, like pillows in the sky,",
            "Singing gentle sleepy songs as they drift on high!",
            "Count the stars now one by one, one and two and three,",
            "Rest your head and drift away, as peaceful as can be!",
        ]
        outro_lines = [
            "Close your eyes and go to sleep, starry dreams are near,",
            "We will watch over you, safe and happy here!",
            "Goodnight to our little star, goodnight to the skies,",
            "Time for sweetest dreams to come as you close your eyes!",
        ]
        char_app = "Glowing golden 3D cartoon star with gentle smiling face and soft sparkling fairy dust trails."
        char_clothing = "Golden glitter rim and soft celestial aura"
        char_anims = ["float", "glow", "dance", "wave"]

    elif is_dino:
        char_id = "dino_dan"
        char_name = "Dino Dan"
        species = "animal"
        title = "Roar Like a Friendly Dino! 🦖🌴 | Toddler Stomp & Dance Song"
        env_name = "Prehistoric Pastel Playground"
        v1_lines = [
            "Stomp stomp stomp with your big green feet,",
            "Dino Dan is dancing to the prehistoric beat!",
            "Flap your little dino arms and give a friendly roar,",
            "Jumping on the mossy stones across the jungle floor!",
        ]
        ch_lines = [
            "Roar roar roar, having so much fun,",
            "Friendly little dinosaurs dancing in the sun!",
            "Wiggle wiggle dino tail, spin in a big round,",
            "Listen to the happy little dinosaur sound!",
        ]
        v2_lines = [
            "Stomping like a Brontosaurus, tall as any tree,",
            "Flapping like a Pterodactyl, happy as can be!",
            "All our little prehistoric friends are jumping high,",
            "Reaching for the cotton candy clouds up in the sky!",
        ]
        bridge_lines = [
            "Wiggle your little dino tail, shake it to and fro,",
            "Tip-toe like a velociraptor, sneaking soft and slow!",
            "Now give a giant dino leap, reaching for the trees,",
            "Dancing with the dino friends in the jungle breeze!",
        ]
        v3_lines = [
            "Triceratops has three big horns and gives a gentle nod,",
            "Stomping to the dino groove with the dino squad!",
            "Herbivore and carnivore, all friends together now,",
            "Dino Dan takes a big smiling toddler dino bow!",
        ]
        outro_lines = [
            "Now the dino sun is setting, time to rest your claws,",
            "Fold your happy dino wings and tuck your sleepy paws!",
            "Thank you Dino Dan for dancing with us all today,",
            "Tomorrow we will have another dino game to play!",
        ]
        char_app = "Adorable emerald green baby T-Rex with huge round curious eyes and soft rounded toddler scales."
        char_clothing = "Bright yellow toddler sneakers and colorful spots"
        char_anims = ["stomp", "roar", "bounce", "tail_wag", "spin"]

    elif is_train:
        char_id = "toto_train"
        char_name = "Toto the Train"
        species = "vehicle"
        title = "Choo Choo Train Adventure! 🚂💨 | 3D Kids Nursery Rhyme"
        env_name = "Rainbow Railway Valley"
        v1_lines = [
            "Choo choo comes the friendly train, rolling down the track,",
            "Bringing lots of happiness there and bringing it back!",
            "Hear the shiny whistle blow, toot toot toot so clear,",
            "Every little friend is welcome, happy to be here!",
        ]
        ch_lines = [
            "Chugga chugga choo choo, chugga chugga choo choo,",
            "Rolling through the valleys where the skies are bright and blue!",
            "Clap your hands and tap your feet, sing along the way,",
            "Toto Train is taking us to have a lovely day!",
        ]
        v2_lines = [
            "Past the rolling green hills, under rainbow skies,",
            "Seeing all the butterflies flutter with surprise!",
            "Ring the shiny golden bell, ding dong ding dong chime,",
            "Every single journey is a happy storytime!",
        ]
        bridge_lines = [
            "Clickety-clack, clickety-clack, speeding down the rail,",
            "Carrying cheerful cargo cars and buckets of colorful mail!",
            "Over the bridge and through the tunnel, hear the whistle blow,",
            "Toto Train is having fun, watch the engine glow!",
        ]
        v3_lines = [
            "Conductor waves his friendly flag, green means time to go,",
            "Chugging past the snowy peaks where gentle breezes blow!",
            "Toot toot goes the happy horn, waving left and right,",
            "Every little railway stop is filled with pure delight!",
        ]
        outro_lines = [
            "Now we are back at Station Home, wave goodbye with cheer,",
            "Thank you little friendly train for bringing sunshine here!",
            "Rest your wheels until tomorrow, have a restful night,",
            "Everything is peaceful and everything is bright!",
        ]
        char_app = "Cute rounded 3D vehicle with vibrant gloss materials, bright cartoon eyes, and playful proportions."
        char_clothing = "Cheerful striped conductor scarf and golden bell"
        char_anims = ["chug", "whistle", "bounce", "wave"]

    elif is_count:
        char_id = "numby_bunny"
        char_name = "Numby Bunny"
        species = "animal"
        title = "Count 1 to 10 with Numby Bunny! 🔢🐰 | Preschool Numbers Song"
        env_name = "Number Balloon Meadow"
        v1_lines = [
            "One two three, count along with me,",
            "Hopping with our bunny friends, happy as can be!",
            "Four five six, counting carrots in a row,",
            "Watch the numbers in the air begin to gently glow!",
        ]
        ch_lines = [
            "Counting numbers is so fun, one by one by one,",
            "Counting all together underneath the golden sun!",
            "Seven, eight, nine and ten, clap and jump again,",
            "Sing our happy number song with all our little friends!",
        ]
        v2_lines = [
            "One little butterfly, two little bees,",
            "Three little apples growing on the apple trees!",
            "Four bouncy balls and five friendly kites,",
            "Counting all our lovely toys with happy cheers and lights!",
        ]
        bridge_lines = [
            "Let us count our fingers, one, two, three, four, five,",
            "Wiggle them all together, happy and alive!",
            "Six, seven, eight, nine, ten, clap your hands so loud,",
            "Numby Bunny is so proud of our clever crowd!",
        ]
        v3_lines = [
            "Count the bouncy colorful balls jumping on the floor,",
            "One and two and three and four, can you count some more?",
            "Count the shiny yellow stars dancing overhead,",
            "Ten big stars are shining down as we get ready for bed!",
        ]
        outro_lines = [
            "Ten big claps for everyone, you did a super job,",
            "Counting all the way to ten with Numby and the squad!",
            "Wave goodbye with happy smiles, learning every day,",
            "Counting numbers is our favorite game to always play!",
        ]
        char_app = "Fluffy pastel blue baby bunny holding colorful wooden number blocks with big floppy ears."
        char_clothing = "Orange dungarees with number badges"
        char_anims = ["hop", "count", "clap", "bounce"]

    elif is_chanda:
        char_id = "chanda_mama"
        char_name = "Chanda Mama"
        species = "celestial"
        title = "चंदा मामा दूर के! 🌙✨ | Chanda Mama Pyare 3D Hindi Rhyme"
        env_name = "Starry Terrace of Dreams"
        v1_lines = [
            "चंदा मामा दूर के, पुए पकाएं बूर के,",
            "आप खाएं थाली में, मुन्ने को दें प्याली में!",
            "प्याली गई टूट, मुन्ना गया रूठ,",
            "लाएंगे नई प्यालियां, बजा बजा के तालियां!",
        ]
        ch_lines = [
            "चंदा मामा, ओ प्यारे चंदा मामा,",
            "आओ हमारे घर, पहनो सुंदर जामा!",
            "हंसते-हंसते गाओ तुम, मीठी लोरी सुनाओ तुम,",
            "सारे तारे चमक रहे, संग में नाच दिखाओ तुम!",
        ]
        v2_lines = [
            "मुन्ने को मनाएंगे, मीठी खीर खिलाएंगे,",
            "चांदी के झूले में, मुन्ने को झुलाएंगे!",
            "उड़ती आई परियां, संग में लाईं खुशियां,",
            "चंदा मामा मुस्कुराए, चमकीं सारी बगियां!",
        ]
        bridge_lines = [
            "आसमान में चमके तारे, जैसे मोती प्यारे-प्यारे,",
            "चंदा मामा मुस्कुराए, नन्हे बच्चों को बुलाए!",
            "ठंडी-ठंडी मीठी हवा, लोरी गाए प्यारी,",
            "सो जाओ मेरे नन्हे मुन्ने, रात आई न्यारी!",
        ]
        v3_lines = [
            "चांदी का रथ लेकर मामा, आए धरती के द्वार,",
            "सब बच्चों को प्यार दिया, बांटा ढेर सारा दुलार!",
            "हाथ जोड़कर करें नमस्ते, चंदा मामा प्यारे,",
            "सदा हमारे घर में आएं, खुशियों के उजियारे!",
        ]
        outro_lines = [
            "सो जा मेरे प्यारे लल्ला, रात सुहानी आई,",
            "चंदा मामा ने आकाश में तारों की चादर बिछाई!",
            "मीठे-मीठे सपनों में अब खो जाओ तुम,",
            "शुभ रात्रि प्यारे बच्चों, प्यार से सो जाओ तुम!",
        ]
        char_app = "Smiling 3D crescent moon with kind grandfatherly eyes wearing a golden crown and silver kurta."
        char_clothing = "Silver celestial kurta and glowing crown"
        char_anims = ["glow", "swing", "smile", "wave"]

    else:
        # UNIVERSAL THEMATIC DYNAMIC GENERATOR (Uses the user actual topic name and keywords!)
        first_w = word_list[0] if word_list else "hero"
        char_id = f"buddy_{first_w}"
        char_name = f"Buddy {clean_topic.split()[0]}"
        species = "character"
        title = f"{clean_topic} 🎶✨ | 3D Kids Sing-Along Nursery Rhyme"
        env_name = f"Magical {clean_topic} Wonderland"
        v1_lines = [
            f"Welcome to our sunny world, {clean_topic} is here today,",
            "Singing cheerful nursery songs as we dance and play!",
            "Look at all our happy friends waving in the sun,",
            f"Singing about {clean_topic}, learning is so fun!",
        ]
        ch_lines = [
            "Sing along together now, happy as can be,",
            f"Loving {clean_topic} today, for you and for me!",
            "Clap your hands and spin around with a joyful cheer,",
            "Every single friend is welcome, happy to be here!",
        ]
        v2_lines = [
            "Past the rolling green hills, under rainbow skies,",
            f"Exploring {clean_topic} with wonder in our eyes!",
            "Tap your toes and bounce along, smiling big and bright,",
            "Every single story is a magical delight!",
        ]
        bridge_lines = [
            f"Round and round, bounce along, celebrating {clean_topic},",
            "Dancing with our joyful friends, full of rhythm and music!",
            "Clap to the beat, one two three, jump up in the air,",
            "Happiness and smiling faces blooming everywhere!",
        ]
        v3_lines = [
            f"Learning every single day with our friend {char_name},",
            "Every moment is exciting, like a sunny game!",
            f"Thank you for this wonderful song about {clean_topic} today,",
            "We will keep on singing bright every time we play!",
        ]
        outro_lines = [
            f"Now it is time to wave goodbye to {clean_topic} today,",
            "Thank you little friends for joining us to play!",
            "Have a restful quiet night, sweet dreams in your head,",
            "Everything is peaceful now as we go to bed!",
        ]
        char_app = f"Cute rounded 3D preschool character with bright curious eyes and friendly smile celebrating {clean_topic}."
        char_clothing = "Vibrant preschool overalls and colorful sneakers"
        char_anims = ["dance", "bounce", "wave", "smile"]

    # DURATION-AWARE VERSE & CHAPTER ASSEMBLY
    if target_dur <= 1.2:
        # ~1 Minute (Short / Viral format: 4 stanzas, 16 lines)
        verses = [
            {"section": "Verse 1", "lines": v1_lines, "character": char_name, "action": "bounces to rhythm"},
            {"section": "Chorus", "lines": ch_lines, "character": char_name, "action": "spins and dances"},
            {"section": "Verse 2", "lines": v2_lines, "character": char_name, "action": "moves side to side"},
            {"section": "Outro", "lines": outro_lines, "character": char_name, "action": "waves farewell under twilight stars"},
        ]
        chapters = [
            {"time": "00:00", "title": "Welcome & Intro"},
            {"time": "00:15", "title": "Verse 1: Singing Along"},
            {"time": "00:30", "title": "Happy Dance Chorus"},
            {"time": "00:45", "title": "Verse 2: Fun Action"},
            {"time": "01:00", "title": "Outro & Goodbye"},
        ]
    elif target_dur <= 2.5:
        # ~2 Minutes (Standard Nursery Rhyme: 9 stanzas, 30 lines)
        intro_lines = [
            f"Are you ready to sing about {clean_topic}?",
            f"Let us dance with {char_name}!",
        ]
        verses = [
            {"section": "Intro", "lines": intro_lines, "character": char_name, "action": "waves excitedly"},
            {"section": "Verse 1", "lines": v1_lines, "character": char_name, "action": "bounces to rhythm"},
            {"section": "Chorus", "lines": ch_lines, "character": char_name, "action": "spins and dances"},
            {"section": "Verse 2", "lines": v2_lines, "character": char_name, "action": "moves side to side"},
            {"section": "Chorus", "lines": ch_lines, "character": char_name, "action": "spins and dances"},
            {"section": "Bridge", "lines": bridge_lines, "character": char_name, "action": "bubbly disco dance"},
            {"section": "Verse 3", "lines": v3_lines, "character": char_name, "action": "celebrates with joyful gestures"},
            {"section": "Chorus", "lines": ch_lines, "character": char_name, "action": "grand group dance"},
            {"section": "Outro", "lines": outro_lines, "character": char_name, "action": "waves farewell under twilight stars"},
        ]
        chapters = [
            {"time": "00:00", "title": "Welcome & Musical Intro"},
            {"time": "00:20", "title": "Verse 1: Sing Along"},
            {"time": "00:40", "title": "Happy Dance Chorus"},
            {"time": "01:00", "title": "Verse 2: Action Play"},
            {"time": "01:25", "title": "Bridge: Rhythm Groove"},
            {"time": "01:45", "title": "Verse 3 & Big Chorus"},
            {"time": "02:00", "title": "Outro & Goodbye"},
        ]
    else:
        # 3–5 Minutes (Extended format: 11 stanzas, 40 lines)
        intro_lines = [
            f"Welcome little friends to our magical song world!",
            f"Get ready to dance to {clean_topic}!",
        ]
        pre_chorus = [
            "Get ready now, clap one two three,",
            f"Sing along with {char_name}, happy and free!",
        ]
        verses = [
            {"section": "Intro", "lines": intro_lines, "character": char_name, "action": "greets viewers with musical chimes"},
            {"section": "Verse 1", "lines": v1_lines, "character": char_name, "action": "bounces to rhythm"},
            {"section": "Pre-Chorus", "lines": pre_chorus, "character": char_name, "action": "claps hands to tempo"},
            {"section": "Chorus", "lines": ch_lines, "character": char_name, "action": "spins and dances"},
            {"section": "Verse 2", "lines": v2_lines, "character": char_name, "action": "moves forward"},
            {"section": "Pre-Chorus", "lines": pre_chorus, "character": char_name, "action": "claps hands to tempo"},
            {"section": "Chorus", "lines": ch_lines, "character": char_name, "action": "spins and dances"},
            {"section": "Bridge", "lines": bridge_lines, "character": char_name, "action": "dynamic rhythm dance"},
            {"section": "Verse 3", "lines": v3_lines, "character": char_name, "action": "interactive toddler choreography"},
            {"section": "Chorus", "lines": ch_lines, "character": char_name, "action": "energy peak dance"},
            {"section": "Outro", "lines": outro_lines, "character": char_name, "action": "waves farewell under twilight stars"},
        ]
        chapters = [
            {"time": "00:00", "title": "Welcome & Musical Overture"},
            {"time": "00:30", "title": "Verse 1: Learning Rhythm"},
            {"time": "01:00", "title": "Happy Dance Chorus"},
            {"time": "01:30", "title": "Verse 2: Playful Adventure"},
            {"time": "02:00", "title": "Bridge: Musical Break"},
            {"time": "02:30", "title": "Verse 3 & Big Dance"},
            {"time": f"{int(target_dur):02d}:00", "title": "Grand Finale & Outro"},
        ]

    NL = chr(10)
    lyrics_full = (NL + NL).join(f"[{v['section']}]{NL}" + NL.join(v["lines"]) for v in verses)

    return {
        "title": title,
        "description": f"""Sing and dance with {char_name} in this joyful, original nursery rhyme about {clean_topic}!

🎵 LYRICS:
{lyrics_full}

#nurseryrhymes #kidssongs #toddlers #preschool""",
        "chapters": chapters,
        "hashtags": ["#nurseryrhymes", "#kidssongs", f"#{clean_topic.replace(' ', '').lower()}", "#preschool"],
        "tags": [clean_topic.lower(), f"{clean_topic.lower()} song", "nursery rhymes", "kids songs", "toddler songs", "preschool animation", "3d cartoon"],
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
                "appearance": char_app,
                "colors": ["#facc15", "#2563eb", "#ef4444"],
                "clothing": char_clothing,
                "face": "Large expressive cartoon eyes with specular highlights, rosy cheeks, friendly curved smile",
                "personality": "Enthusiastic, caring, safe guide for toddlers",
                "voice": "tenor_cheerful",
                "animation_set": char_anims,
            }
        ],
        "environments": [
            {
                "id": "env_01",
                "name": env_name,
                "description": f"Vibrant {env_name} with rolling pastel hills, playful props, and warm golden sunlight",
            }
        ],
        "music_style": "120 BPM upbeat preschool pop, energetic marimba, joyful acoustic guitar, handclaps",
        "voice_style": "Warm cheerful preschool storyteller with clear articulation",
        "thumbnail_prompt": f"Cute 3D CGI cartoon animation of {char_name} smiling happily in {env_name}, 8k vibrant lighting, high CTR YouTube Kids thumbnail",
        "target_audience": target_age,
        "educational_angle": "Rhythm recognition, phonics, vocabulary and cooperative play",
        "visual_bible": {
            "visual_style": "3D Cartoon Stylized Preschool Animation",
            "render_style": "Soft diffuse lighting, glossy toy-like materials, vibrant saturated palette",
            "lighting_style": "Bright warm daylight with subtle rim highlights",
            "camera_style": "Dynamic low-angle eye-level tracking with gentle push-ins",
            "environment_style": "Rounded low-poly hills, pastel skies, chunky props",
        },
    }
