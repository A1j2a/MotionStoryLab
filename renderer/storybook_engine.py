import os
import math
import subprocess
import shutil
from typing import Dict, Any, List
from renderer.compositor import get_ffmpeg_path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


def _create_storybook_frame(
    topic: str,
    scene_number: int,
    verse_text: str,
    output_png: str,
    width: int = 1280,
    height: int = 720,
):
    """
    Renders a vibrant, anti-aliased preschool illustration frame using Pillow.
    Market-standard Cocomelon / Super Simple Songs styling.
    """
    t = topic.lower()
    is_dino = any(w in t for w in ["dino", "dinosaur", "rex", "t-rex", "jurassic", "escape", "monster", "chase"])
    is_star = any(w in t for w in ["star", "moon", "night", "sky", "twinkle"]) and not is_dino
    is_bus = any(w in t for w in ["bus", "car", "drive", "road", "wheel", "wheels"]) and not is_dino
    is_farm = any(w in t for w in ["cow", "duck", "farm", "sheep", "animal", "old macdonald"]) and not is_dino
    is_fruit = any(w in t for w in ["fruit", "apple", "banana", "berry", "food"]) and not is_dino

    img = Image.new("RGB", (width, height), (56, 189, 248))
    draw = ImageDraw.Draw(img)

    # 1. Sky Gradient & Celestial Object
    if is_dino:
        # Prehistoric Jurassic Sky (Amber/Orange Sunset with Volcano Glow)
        for y in range(height):
            ratio = y / height
            r = int(251 + (249 - 251) * ratio)
            g = int(146 + (115 - 146) * ratio)
            b = int(60 + (22 - 60) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        # Distant Volcano with Glowing Lava Peak
        draw.polygon([(900, 520), (1050, 240), (1200, 520)], fill=(87, 83, 78))
        draw.polygon([(1020, 260), (1050, 240), (1080, 260)], fill=(239, 68, 68))
        # Volcano smoke puffs
        for sx, sy, sr in [(1050, 210, 25), (1065, 160, 35), (1090, 110, 48)]:
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 113, 108, 180))
        # Jurassic Palm Trees in background
        for px in [120, 320, 750]:
            draw.line([(px, 350), (px, 540)], fill=(120, 53, 15), width=12)
            for leaf_ang in [-40, -15, 10, 35]:
                rad = math.radians(leaf_ang)
                draw.arc([px - 80, 310, px + 80, 410], 180, 360, fill=(34, 197, 94), width=14)
        series_title = "🚌 BUS ESCAPE FROM GIANT DINOSAUR! 🦖"
    elif is_star:
        # Midnight starry sky
        for y in range(height):
            ratio = y / height
            r = int(11 + (28 - 11) * ratio)
            g = int(19 + (37 - 19) * ratio)
            b = int(43 + (65 - 43) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        # Crescent / Glowing Moon
        draw.ellipse([1020, 60, 1160, 200], fill=(254, 240, 138))
        draw.ellipse([990, 45, 1120, 185], fill=(15, 23, 42))  # Shadow to create crescent
        # Scattered Stars
        stars_pos = [(140, 100), (320, 150), (480, 80), (680, 120), (880, 70), (220, 260), (790, 220)]
        for sx, sy in stars_pos:
            draw.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill=(255, 255, 255))
            draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(254, 240, 138))
        series_title = "⭐ TWINKLE TWINKLE LITTLE STAR ⭐"
    else:
        # Sunny sky gradient
        for y in range(height):
            ratio = y / height
            r = int(56 + (186 - 56) * ratio)
            g = int(189 + (230 - 189) * ratio)
            b = int(248 + (253 - 248) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        # Golden Sun
        draw.ellipse([1030, 45, 1190, 205], fill=(253, 224, 71))
        # Cartoon Clouds
        for cx, cy in [(180, 120), (620, 95), (860, 150)]:
            draw.ellipse([cx, cy, cx + 120, cy + 60], fill=(255, 255, 255))
            draw.ellipse([cx + 35, cy - 25, cx + 95, cy + 45], fill=(255, 255, 255))

    # 2. Rolling Green Hills / Background
    if is_dino:
        draw.pieslice([-100, 420, 720, 1020], 180, 360, fill=(22, 101, 52))
        draw.pieslice([380, 450, 1420, 1120], 180, 360, fill=(21, 128, 61))
    elif is_star:
        draw.pieslice([-100, 440, 750, 1050], 180, 360, fill=(30, 41, 59))
        draw.pieslice([400, 470, 1420, 1120], 180, 360, fill=(15, 23, 42))
    else:
        draw.pieslice([-100, 420, 720, 1020], 180, 360, fill=(74, 222, 128))
        draw.pieslice([380, 460, 1420, 1120], 180, 360, fill=(34, 197, 94))

    # 3. Ground / Road
    if is_dino or is_bus:
        # Asphalt Road with Dash Marks & Speed Lines
        draw.rectangle([0, 615, width, height], fill=(71, 85, 105))
        for rx in range(30, width, 140):
            draw.rectangle([rx, 660, rx + 75, 672], fill=(255, 255, 255))
        if not is_dino:
            series_title = "🚌 BUSTER THE BUS ADVENTURES 🚌"
    elif is_farm:
        draw.rectangle([0, 620, width, height], fill=(180, 83, 9))
        series_title = "🐮 OLD MACDONALD'S HAPPY FARM 🐮"
    elif is_fruit:
        draw.rectangle([0, 620, width, height], fill=(251, 146, 60))
        series_title = "🍎 DANCING FRUITS SING-ALONG 🍌"
    elif not is_star:
        draw.rectangle([0, 620, width, height], fill=(22, 163, 74))
        series_title = f"🎈 {topic.strip().upper()} 🎈"

    # 4. Animated Hero Characters
    if is_dino:
        # A) GIANT T-REX DINOSAUR (Running on Left/Center behind Bus)
        dx, dy = 160, 220
        # Giant Green Body
        draw.ellipse([dx, dy + 60, dx + 260, dy + 320], fill=(34, 197, 94), outline=(21, 128, 61), width=5)
        # Yellow Belly
        draw.ellipse([dx + 110, dy + 100, dx + 240, dy + 280], fill=(253, 224, 71))
        # Giant Dinosaur Head with Big Open Smiling Jaws
        draw.rounded_rectangle([dx + 120, dy - 40, dx + 330, dy + 110], radius=40, fill=(34, 197, 94), outline=(21, 128, 61), width=5)
        # Big Cartoon Friendly Eyes
        draw.ellipse([dx + 190, dy - 25, dx + 240, dy + 25], fill=(255, 255, 255), outline=(30, 41, 59), width=3)
        draw.ellipse([dx + 215, dy - 12, dx + 235, dy + 12], fill=(30, 41, 59))
        draw.ellipse([dx + 225, dy - 6, dx + 232, dy + 2], fill=(255, 255, 255))
        # Sharp Cartoon Teeth
        for tx in range(dx + 170, dx + 310, 25):
            draw.polygon([(tx, dy + 65), (tx + 12, dy + 85), (tx + 24, dy + 65)], fill=(255, 255, 255))
        # Cute Tiny T-Rex Arms
        draw.ellipse([dx + 240, dy + 140, dx + 300, dy + 180], fill=(34, 197, 94), outline=(21, 128, 61), width=4)
        # Powerful Stomping Legs
        draw.rectangle([dx + 40, dy + 260, dx + 110, dy + 380], fill=(34, 197, 94))
        draw.ellipse([dx + 20, dy + 360, dx + 130, dy + 410], fill=(34, 197, 94))
        draw.rectangle([dx + 140, dy + 280, dx + 210, dy + 390], fill=(22, 163, 74))

        # B) SPEEDING ADVENTURE BUS (Ahead on Right)
        bx, by = 680, 310
        bw, bh = 480, 240
        # Turbo Exhaust Flames
        draw.polygon([(bx - 70, by + 160), (bx - 20, by + 140), (bx - 20, by + 180)], fill=(239, 68, 68))
        draw.polygon([(bx - 50, by + 160), (bx - 20, by + 148), (bx - 20, by + 172)], fill=(251, 191, 36))
        # Yellow Bus Body
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=40, fill=(250, 204, 21), outline=(202, 138, 4), width=5)
        # Stripes
        draw.rectangle([bx, by + 110, bx + bw, by + 125], fill=(202, 138, 4))
        draw.rectangle([bx, by + 140, bx + bw, by + 155], fill=(202, 138, 4))
        # Windows with Excited Passengers
        for wx in [bx + 40, bx + 150, bx + 260, bx + 370]:
            draw.rounded_rectangle([wx, by + 30, wx + 95, by + 100], radius=14, fill=(224, 242, 254), outline=(2, 132, 199), width=3)
        # Wheels
        for whx in [bx + 80, bx + 360]:
            draw.ellipse([whx, by + bh - 35, whx + 95, by + bh + 60], fill=(30, 41, 59))
            draw.ellipse([whx + 22, by + bh - 10, whx + 73, by + bh + 38], fill=(148, 163, 184))
        # Expressive Surprised Alert Eyes (Speeding!)
        draw.ellipse([bx + bw - 55, by + 110, bx + bw - 15, by + 155], fill=(255, 255, 255), outline=(30, 41, 59), width=3)
        draw.ellipse([bx + bw - 40, by + 122, bx + bw - 22, by + 142], fill=(2, 132, 199))
        draw.arc([bx + bw - 75, by + 155, bx + bw - 20, by + 190], 0, 180, fill=(30, 41, 59), width=4)

    elif is_bus:
        # Buster the Yellow Bus
        bx, by = 310, 270
        bw, bh = 660, 290
        # Main Yellow Body
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=45, fill=(250, 204, 21), outline=(202, 138, 4), width=5)
        # Decorative Stripes
        draw.rectangle([bx, by + 140, bx + bw, by + 155], fill=(202, 138, 4))
        draw.rectangle([bx, by + 170, bx + bw, by + 185], fill=(202, 138, 4))
        # Windows
        for wx in [bx + 50, bx + 190, bx + 330, bx + 470]:
            draw.rounded_rectangle([wx, by + 35, wx + 115, by + 130], radius=16, fill=(224, 242, 254), outline=(2, 132, 199), width=4)
        # Wheels
        for whx in [bx + 110, bx + 490]:
            draw.ellipse([whx, by + bh - 40, whx + 115, by + bh + 75], fill=(30, 41, 59))
            draw.ellipse([whx + 28, by + bh - 12, whx + 87, by + bh + 47], fill=(148, 163, 184))
            draw.ellipse([whx + 46, by + bh + 6, whx + 69, by + bh + 29], fill=(241, 245, 249))
        # Friendly Front Eyes & Smile
        draw.ellipse([bx + bw - 70, by + 150, bx + bw - 25, by + 195], fill=(255, 255, 255), outline=(30, 41, 59), width=3)
        draw.ellipse([bx + bw - 52, by + 162, bx + bw - 33, by + 183], fill=(2, 132, 199))
        draw.ellipse([bx + bw - 44, by + 167, bx + bw - 38, by + 173], fill=(255, 255, 255))
        # Smile
        draw.arc([bx + bw - 90, by + 195, bx + bw - 30, by + 235], 0, 180, fill=(30, 41, 59), width=5)
        # Rosy Cheek
        draw.ellipse([bx + bw - 95, by + 205, bx + bw - 75, by + 220], fill=(244, 63, 94))
    elif is_star:
        # Giant Twinkling Star Character
        cx, cy = 640, 360
        r_outer, r_inner = 170, 75
        points = []
        for i in range(10):
            r = r_outer if i % 2 == 0 else r_inner
            angle = i * (math.pi / 5) - math.pi / 2
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        draw.polygon(points, fill=(250, 204, 21), outline=(234, 179, 8))
        # Cute Kawaii Eyes
        draw.ellipse([cx - 50, cy - 25, cx - 15, cy + 15], fill=(30, 41, 59))
        draw.ellipse([cx + 15, cy - 25, cx + 50, cy + 15], fill=(30, 41, 59))
        draw.ellipse([cx - 40, cy - 20, cx - 25, cy - 5], fill=(255, 255, 255))
        draw.ellipse([cx + 25, cy - 20, cx + 40, cy - 5], fill=(255, 255, 255))
        # Kawaii Smile
        draw.arc([cx - 25, cy + 5, cx + 25, cy + 45], 0, 180, fill=(30, 41, 59), width=5)
        # Rosy Cheeks
        draw.ellipse([cx - 70, cy + 15, cx - 45, cy + 32], fill=(251, 113, 133))
        draw.ellipse([cx + 45, cy + 15, cx + 70, cy + 32], fill=(251, 113, 133))
    elif is_farm:
        # Cute Daisy Cow
        cx, cy = 640, 380
        # Cow Body
        draw.rounded_rectangle([cx - 160, cy - 100, cx + 160, cy + 130], radius=50, fill=(255, 255, 255), outline=(30, 41, 59), width=5)
        # Cow Spots
        draw.ellipse([cx - 130, cy - 70, cx - 50, cy], fill=(30, 41, 59))
        draw.ellipse([cx + 40, cy - 20, cx + 130, cy + 70], fill=(30, 41, 59))
        # Cute Snout
        draw.rounded_rectangle([cx - 80, cy + 10, cx + 80, cy + 90], radius=30, fill=(251, 182, 206), outline=(30, 41, 59), width=4)
        draw.ellipse([cx - 35, cy + 40, cx - 15, cy + 60], fill=(30, 41, 59))
        draw.ellipse([cx + 15, cy + 40, cx + 35, cy + 60], fill=(30, 41, 59))
        # Big Cartoon Eyes
        draw.ellipse([cx - 65, cy - 70, cx - 20, cy - 25], fill=(30, 41, 59))
        draw.ellipse([cx + 20, cy - 70, cx + 65, cy - 25], fill=(30, 41, 59))
        draw.ellipse([cx - 50, cy - 65, cx - 35, cy - 50], fill=(255, 255, 255))
        draw.ellipse([cx + 35, cy - 65, cx + 50, cy - 50], fill=(255, 255, 255))
        # Horns
        draw.pieslice([cx - 120, cy - 140, cx - 70, cy - 70], 210, 330, fill=(251, 191, 36), outline=(30, 41, 59))
        draw.pieslice([cx + 70, cy - 140, cx + 120, cy - 70], 210, 330, fill=(251, 191, 36), outline=(30, 41, 59))
    else:
        # Friendly Dancing Character
        cx, cy = 640, 370
        draw.ellipse([cx - 130, cy - 130, cx + 130, cy + 130], fill=(244, 63, 94), outline=(190, 18, 60), width=5)
        draw.ellipse([cx - 60, cy - 40, cx - 20, cy], fill=(255, 255, 255))
        draw.ellipse([cx + 20, cy - 40, cx + 60, cy], fill=(255, 255, 255))
        draw.ellipse([cx - 45, cy - 30, cx - 30, cy - 15], fill=(15, 23, 42))
        draw.ellipse([cx + 35, cy - 30, cx + 50, cy - 15], fill=(15, 23, 42))
        draw.arc([cx - 45, cy + 10, cx + 45, cy + 60], 0, 180, fill=(255, 255, 255), width=6)

    # 5. Top Series Banner
    banner_color = (15, 23, 42) if is_star else (2, 132, 199)
    draw.rounded_rectangle([140, 35, width - 140, 95], radius=24, fill=banner_color)

    # 6. Bottom Lyric Karaoke Card
    draw.rounded_rectangle([120, height - 125, width - 120, height - 35], radius=22, fill=(255, 255, 255), outline=(226, 232, 240), width=2)

    # Typography
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
    ]
    font_bold = None
    font_med = None
    for p in font_paths:
        if os.path.exists(p):
            try:
                font_bold = ImageFont.truetype(p, 30)
                font_med = ImageFont.truetype(p, 26)
                break
            except Exception:
                continue

    if not font_bold:
        font_bold = ImageFont.load_default()
        font_med = ImageFont.load_default()

    clean_verse = verse_text.replace("\n", " ").strip()[:70] or f"Scene {scene_number}: Sing Along with Friends!"
    draw.text((width / 2, 65), series_title, font=font_bold, fill=(255, 255, 255), anchor="mm")
    draw.text((width / 2, height - 80), clean_verse, font=font_med, fill=(15, 23, 42), anchor="mm")

    os.makedirs(os.path.dirname(os.path.abspath(output_png)), exist_ok=True)
    img.save(output_png, quality=95)
    return output_png


def render_illustrated_scene(
    scene_number: int,
    topic: str,
    verse_text: str,
    duration_sec: float,
    output_mp4: str,
    width: int = 1280,
    height: int = 720,
    fps: int = 24,
) -> str:
    """
    Renders a high-definition, market-standard preschool animation clip (1280x720 24fps)
    featuring vibrant storybook visuals, dynamic Ken Burns motion, and synchronized karaoke lyric cards.
    Replaces slow and outdated procedural Blender blocks.
    """
    ffmpeg_bin = get_ffmpeg_path()
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)

    temp_png = output_mp4.replace(".mp4", "_frame.png")

    if HAS_PILLOW:
        _create_storybook_frame(topic, scene_number, verse_text, temp_png, width=width, height=height)
    else:
        # Fallback SVG/color
        pass

    total_frames = max(1, int(duration_sec * fps))

    # Dynamic camera movements by scene number
    if scene_number == 1:
        # Slow cinematic zoom in
        zoom_filter = f"scale={width}:{height},zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif scene_number == 2:
        # Dynamic tracking pan right
        zoom_filter = f"scale={width}:{height},zoompan=z=1.08:d={total_frames}:x='if(lte(on,1),(iw-iw/zoom)/2,x+1.2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif scene_number == 3:
        # Smooth zoom out to reveal world
        zoom_filter = f"scale={width}:{height},zoompan=z='max(1.15-0.0012*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    else:
        # Playful rhythmic bounce
        zoom_filter = f"scale={width}:{height},zoompan=z='1.06+0.03*sin(2*PI*on/48)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

    if os.path.exists(temp_png):
        cmd = [
            ffmpeg_bin, "-y",
            "-loop", "1",
            "-i", temp_png,
            "-t", str(duration_sec),
            "-vf", zoom_filter,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            "-movflags", "+faststart",
            output_mp4,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(temp_png):
            try:
                os.remove(temp_png)
            except OSError:
                pass
        if res.returncode == 0 and os.path.exists(output_mp4):
            return output_mp4

    # Robust fallback: solid color if anything fails
    fallback_cmd = [
        ffmpeg_bin, "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x48CAE4:s={width}x{height}:d={duration_sec}:r={fps}",
        "-t", str(duration_sec),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_mp4,
    ]
    subprocess.run(fallback_cmd, check=True)
    return output_mp4
