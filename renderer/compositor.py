import os
import math
import shutil
import subprocess
from typing import List, Optional


def get_ffmpeg_path() -> str:
    return shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"


def get_ffprobe_path() -> str:
    return shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"


def get_video_duration(video_path: str) -> float:
    """Returns duration of video in seconds using ffprobe, or 0.0 on failure."""
    if not os.path.exists(video_path):
        return 0.0
    ffprobe_bin = get_ffprobe_path()
    try:
        cmd = [
            ffprobe_bin,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0 and res.stdout.strip():
            return float(res.stdout.strip())
    except Exception:
        pass
    return 0.0


def extract_final_frame(video_path: str, output_image_path: str) -> str:
    """
    Extracts the very last frame of a video using FFmpeg for seamless scene continuity (FLF2V).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_image_path)), exist_ok=True)
    ffmpeg_bin = get_ffmpeg_path()

    # Try fast EOF seek first
    cmd = [
        ffmpeg_bin, "-y",
        "-sseof", "-0.15",
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_image_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(output_image_path) and os.path.getsize(output_image_path) > 500:
        return output_image_path

    # Fallback: query duration and seek to (duration - 0.2s)
    dur = get_video_duration(video_path)
    seek_time = max(0.0, dur - 0.2)
    cmd2 = [
        ffmpeg_bin, "-y",
        "-ss", f"{seek_time:.2f}",
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_image_path,
    ]
    subprocess.run(cmd2, capture_output=True, text=True)
    return output_image_path


def extract_frame_at(video_path: str, output_image_path: str, timestamp_sec: float = 1.0) -> str:
    """
    Extracts a representative frame at the specified timestamp for character validation.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_image_path)), exist_ok=True)
    ffmpeg_bin = get_ffmpeg_path()

    cmd = [
        ffmpeg_bin, "-y",
        "-ss", f"{max(0.0, timestamp_sec):.2f}",
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_image_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    return output_image_path


def adjust_video_duration(input_mp4: str, output_mp4: str, target_duration: float) -> str:
    """
    Adjusts video timing to match target scene duration (e.g. ~8 seconds) without altering SRT timings.
    Uses FFmpeg PTS scaling or trimming/padding.
    """
    if not os.path.exists(input_mp4):
        raise FileNotFoundError(f"Input video not found: {input_mp4}")

    if target_duration <= 0:
        target_duration = 5.0

    current_dur = get_video_duration(input_mp4)
    # If already close within 0.25 seconds, keep as is
    if current_dur > 0 and abs(current_dur - target_duration) < 0.25:
        if os.path.abspath(input_mp4) != os.path.abspath(output_mp4):
            shutil.copy2(input_mp4, output_mp4)
        return output_mp4

    ffmpeg_bin = get_ffmpeg_path()
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)
    temp_out = output_mp4 if os.path.abspath(input_mp4) != os.path.abspath(output_mp4) else output_mp4 + ".dur.mp4"

    if current_dur > 0 and current_dur > target_duration:
        # Trim excess frames to target duration
        cmd = [
            ffmpeg_bin, "-y",
            "-i", input_mp4,
            "-t", f"{target_duration:.3f}",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            temp_out,
        ]
    elif current_dur > 0 and current_dur < target_duration:
        # Scale PTS to smoothly stretch motion to target duration
        scale_factor = target_duration / current_dur
        cmd = [
            ffmpeg_bin, "-y",
            "-i", input_mp4,
            "-vf", f"setpts={scale_factor:.4f}*PTS",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            temp_out,
        ]
    else:
        # Fallback simple duration flag
        cmd = [
            ffmpeg_bin, "-y",
            "-i", input_mp4,
            "-t", f"{target_duration:.3f}",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            temp_out,
        ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(temp_out) and os.path.getsize(temp_out) > 1000:
        if temp_out != output_mp4:
            shutil.move(temp_out, output_mp4)
        return output_mp4
    else:
        if os.path.abspath(input_mp4) != os.path.abspath(output_mp4):
            shutil.copy2(input_mp4, output_mp4)
        return output_mp4


def concatenate_scenes(
    scene_video_paths: List[str],
    output_merged_path: str,
    target_duration: Optional[float] = None,
) -> str:
    """
    Concatenates multiple scene MP4 files into a continuous video matching target duration.
    """
    if not scene_video_paths:
        raise ValueError("No scene videos provided for concatenation")

    os.makedirs(os.path.dirname(os.path.abspath(output_merged_path)), exist_ok=True)

    concat_txt = output_merged_path.replace(".mp4", "_concat.txt")
    
    # If target_duration is set (e.g. 60s, 120s, 300s), repeat scene shots to cover duration
    paths_to_concat = list(scene_video_paths)
    if target_duration and target_duration > 0:
        # Approximate 5.0s per rendered shot
        single_loop_dur = max(5.0, len(scene_video_paths) * 5.0)
        repeats = max(1, math.ceil(target_duration / single_loop_dur))
        paths_to_concat = (scene_video_paths * repeats)

    with open(concat_txt, "w", encoding="utf-8") as f:
        for path in paths_to_concat:
            f.write(f"file '{os.path.abspath(path)}'\n")

    ffmpeg_bin = get_ffmpeg_path()
    cmd = [
        ffmpeg_bin, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt,
    ]
    if target_duration and target_duration > 0:
        cmd.extend(["-t", str(target_duration)])

    cmd.extend([
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_merged_path
    ])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(concat_txt):
        os.remove(concat_txt)

    if res.returncode != 0 or not os.path.exists(output_merged_path):
        raise RuntimeError(f"FFmpeg concat failed: {res.stderr}")

    return output_merged_path


def composite_final_video(
    video_path: str,
    audio_path: str,
    output_final_path: str,
    subtitles_path: Optional[str] = None,
    target_duration: Optional[float] = None,
) -> str:
    """
    Composites final merged video with multi-track audio, synchronized subtitles, and duration control.
    """
    ffmpeg_bin = get_ffmpeg_path()
    os.makedirs(os.path.dirname(os.path.abspath(output_final_path)), exist_ok=True)

    cmd = [
        ffmpeg_bin, "-y",
        "-i", video_path,
        "-i", audio_path,
    ]

    if target_duration and target_duration > 0:
        cmd.extend(["-t", str(target_duration)])

    # Try burning subtitles if srt exists
    if subtitles_path and os.path.exists(subtitles_path):
        sub_escaped = subtitles_path.replace(":", "\\:").replace("'", "\\'")
        cmd.extend([
            "-vf", f"subtitles='{sub_escaped}':force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,MarginV=35'",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output_final_path
        ])
    else:
        cmd.extend([
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output_final_path
        ])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(output_final_path):
        fallback_cmd = [
            ffmpeg_bin, "-y",
            "-i", video_path,
            "-i", audio_path,
        ]
        if target_duration and target_duration > 0:
            fallback_cmd.extend(["-t", str(target_duration)])
        fallback_cmd.extend([
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output_final_path
        ])
        res_fb = subprocess.run(fallback_cmd, capture_output=True, text=True)
        if res_fb.returncode != 0 or not os.path.exists(output_final_path):
            raise RuntimeError(f"FFmpeg compositing failed: {res_fb.stderr}")

    return output_final_path


def generate_thumbnail(video_path: str, output_thumbnail_path: str) -> str:
    """
    Extracts a crisp, vibrant thumbnail JPEG from the generated video.
    """
    ffmpeg_bin = get_ffmpeg_path()
    os.makedirs(os.path.dirname(os.path.abspath(output_thumbnail_path)), exist_ok=True)

    cmd = [
        ffmpeg_bin, "-y",
        "-ss", "00:00:02.0",
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_thumbnail_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(output_thumbnail_path):
        cmd[2] = "00:00:00.5"
        subprocess.run(cmd, capture_output=True, text=True)

    return output_thumbnail_path


def _get_best_font(size: int, bold: bool = True):
    """Safely find and return the best available rounded cartoon/Pixar font for high-CTR thumbnails."""
    from PIL import ImageFont
    font_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
        "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc",
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Trebuchet MS Bold.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def extract_short_thumbnail_title(title: str, topic: str = "") -> str:
    """
    Extracts a super-short, punchy 1 to 3 word headline (max ~16 chars) for YouTube Kids CTR.
    Removes generic filler words, subtitles, emojis, and punctuation so the headline
    never covers or dominates the thumbnail artwork.
    Examples:
      'Bella the blue bus & the fun ride ✨🎶 | 3D Nursery Rhymes' -> 'BLUE BUS!'
      'Rain, Rain, Go Away | Kids Songs 🌧️' -> 'RAIN RAIN!'
      'Twinkle Twinkle Little Star ✨' -> 'LITTLE STAR!'
      'Wheels on the Bus Go Round and Round' -> 'THE BUS!'
      'Cloud Critters & Rainy Friends' -> 'RAIN RAIN!'
    """
    import re
    raw = (title or topic or "").strip()
    for sep in ["|", ":", " - ", "—", "(", "["]:
        if sep in raw:
            raw = raw.split(sep)[0].strip()

    clean = re.sub(r"[^\w\s&]", " ", raw)
    words = [w.strip() for w in clean.split() if w.strip()]

    lower_raw = raw.lower()
    if "bus" in lower_raw:
        if "blue" in lower_raw:
            return "BLUE BUS!"
        return "THE BUS!"
    if "rain" in lower_raw:
        return "RAIN RAIN!"
    if "shark" in lower_raw:
        return "BABY SHARK!"
    if "star" in lower_raw:
        return "LITTLE STAR!"
    if "monkey" in lower_raw:
        return "5 MONKEYS!"
    if "duck" in lower_raw:
        return "5 DUCKS!"
    if "dino" in lower_raw:
        return "DINO FUN!"

    fillers = {
        "NURSERY", "RHYMES", "RHYME", "PRESCHOOL", "SONGS", "SONG",
        "FOR", "KIDS", "CHILDREN", "TODDLERS", "BABY", "ANIMATION",
        "CARTOON", "EPISODE", "3D", "OFFICIAL", "VIDEO", "THE", "AND", "&", "A", "AN"
    }
    meaningful = [w for w in words if w.upper() not in fillers]

    if 1 <= len(meaningful) <= 2:
        return " ".join(meaningful).upper() + "!"
    elif len(meaningful) >= 3:
        return " ".join(meaningful[:2]).upper() + "!"

    if words:
        return " ".join(words[:2]).upper() + "!"
    return "FUN TIME!"


def build_high_ctr_thumbnail_prompt(
    title: str,
    topic: str,
    character_name: str = "Hero",
    appearance: str = "",
    environment: str = "",
) -> str:
    """
    Builds an ultra-high CTR 3D Disney Pixar style YouTube thumbnail prompt based on the specific topic.
    Designed for Midjourney v6, Leonardo, Flux Dev, and DALL-E 3.
    Strictly specifies NO TEXT / NO WATERMARK so that clean typography can be overlaid.
    """
    clean_topic = topic or title or "Preschool Kids Song"
    for sep in ["|", ":", " - ", "—", "(", "["]:
        if sep in clean_topic:
            clean_topic = clean_topic.split(sep)[0].strip()

    clean_lower = clean_topic.lower()

    if "bus" in clean_lower or "wheels" in clean_lower:
        subject = (
            "An adorable cheerful 3D cartoon blue preschool bus with big smiling expressive cartoon eyes "
            "on the windshield, cute friendly face, and rosy cheeks. Happy baby animal passengers (fluffy puppy, smiling bear cub, "
            "playful bunny) peeking joyfully out of colorful open windows and waving"
        )
        setting = (
            "driving merrily along a winding sunny rainbow hilltop road, colorful blooming flowers, "
            "puffy soft white clouds, and a bright glowing rainbow arc in a vibrant turquoise sky with a smiling friendly sun"
        )
    elif "rain" in clean_lower or "cloud" in clean_lower or "storm" in clean_lower:
        subject = (
            "An adorable cute 3D preschool character wearing a glossy bright yellow raincoat and cute rainboots, "
            "holding a vibrant rainbow-striped umbrella, smiling with big sparkling joyful eyes, splashing playfully in clear puddles"
        )
        setting = (
            "a magical cheerful rain shower with sparkling animated raindrops, a friendly smiling cartoon cloud, "
            "and a brilliant glowing rainbow arc bursting through warm golden sunshine"
        )
    elif "dino" in clean_lower:
        subject = (
            "An adorable cute friendly baby 3D cartoon dinosaur with oversized sparkling eyes, "
            "gentle cheerful smile, and vibrant pastel-colored scales, jumping with pure joy"
        )
        setting = (
            "a lush prehistoric preschool wonderland with giant colorful fantasy flowers, soft rounded hills, "
            "sparkling waterfalls, and warm sunny golden rim lighting"
        )
    elif "farm" in clean_lower or "animal" in clean_lower or "macdonald" in clean_lower:
        subject = (
            "A group of adorable cute 3D baby farm animals (smiling baby calf, fluffy yellow chick, playful little lamb) "
            "dancing and smiling happily together with huge expressive eyes"
        )
        setting = (
            "a sunny green farm meadow in front of a cozy red barn, white picket fences, sunflowers, "
            "and a radiant blue sky with gentle fluffy clouds"
        )
    else:
        char_desc = appearance or f"cute lovable 3D animated character {character_name}"
        subject = (
            f"{char_desc}, smiling happily with big expressive sparkling joyful eyes, rosy cheeks, "
            "and an energetic excited welcoming pose"
        )
        setting = (
            f"a vibrant magical preschool world themed around {clean_topic}, filled with playful rounded props, "
            "blooming pastel flowers, sparkling fairy dust, and a glowing colorful rainbow in a sunny sky"
        )

    prompt = (
        f"3D Disney Pixar CGI animation style YouTube Kids Thumbnail artwork for \"{clean_topic}\": "
        f"{subject}. "
        f"Setting: {setting}. "
        f"Visual Quality: 8k ultra-detailed CGI render, vibrant saturated preschool candy palette, "
        f"Unreal Engine 5 aesthetic, soft cinematic sunny rim lighting, volumetric glow, high-CTR YouTube Kids cover composition, "
        f"strictly NO text, NO words, NO letters, NO watermark, NO logo."
    )
    return prompt


def generate_high_ctr_thumbnail(
    title: str = "Kids Nursery Rhyme",
    topic: str = "Preschool Song",
    output_thumbnail_path: str = "thumbnail.jpg",
    video_path: Optional[str] = None,
    aspect_ratio: str = "16:9",
    character_name: str = "Hero",
    character_appearance: Optional[str] = None,
    custom_prompt: Optional[str] = None,
) -> str:
    """
    Generates an ultra-high CTR / high-CPM 3D Pixar Disney style YouTube Kids Thumbnail.
    - Topic-aligned AI prompt generation saved to thumbnail_prompt.txt.
    - AI-generated background (Flux / Fal / Midjourney prompt).
    - NEVER extracts frames from video scenes (user specification: AI generated only).
    - Short, punchy 1 to 2 word headline (e.g. 'BLUE BUS!', 'RAIN RAIN!').
    - Compact, non-intrusive typography that never overpowers or blocks the artwork.
    - Bottom subtitle badge: Golden-yellow 3D pill badge with topic tag.
    """
    import math
    from pathlib import Path
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

    os.makedirs(os.path.dirname(os.path.abspath(output_thumbnail_path)), exist_ok=True)
    is_vertical = (aspect_ratio == "9:16")
    width, height = (1080, 1920) if is_vertical else (1280, 720)

    # 1. Build & Save AI Thumbnail Prompt
    ai_prompt = custom_prompt or build_high_ctr_thumbnail_prompt(
        title=title,
        topic=topic,
        character_name=character_name,
        appearance=character_appearance or "",
    )

    # Save prompt to companion text files
    try:
        prompt_txt = Path(output_thumbnail_path).parent / "thumbnail_prompt.txt"
        prompt_txt.write_text(ai_prompt, encoding="utf-8")
        Path(output_thumbnail_path + ".prompt.txt").write_text(ai_prompt, encoding="utf-8")
    except Exception as pe:
        logger.debug(f"Failed to write thumbnail prompt file: {pe}")

    # 2. Try AI Image Generation (Wan / Fal AI / Flux) if API is configured
    base_img = None
    try:
        from ai.image_provider import get_image_provider, NewAIImageProvider
        img_provider = get_image_provider("ai")
        if isinstance(img_provider, NewAIImageProvider) and img_provider.api_key and "..." not in img_provider.api_key:
            temp_ai_path = output_thumbnail_path + ".ai.jpg"
            if img_provider.generate_image(ai_prompt, temp_ai_path, aspect_ratio=aspect_ratio):
                if os.path.exists(temp_ai_path) and os.path.getsize(temp_ai_path) > 1000:
                    raw_im = Image.open(temp_ai_path).convert("RGB")
                    base_img = raw_im.resize((width, height), Image.Resampling.LANCZOS)
                    try:
                        os.remove(temp_ai_path)
                    except Exception:
                        pass
    except Exception as ai_e:
        logger.debug(f"AI thumbnail background generation skipped: {ai_e}")

    # NOTE: Video frame extraction is STRICTLY EXCLUDED per user specification:
    # "thumbnil video me se nahi lena hai uska topic ke according genrate krna hai ai se".
    # Under no circumstances do we sample frames from video_path.

    # 3. If AI generation is offline / pending, create rich 3D Pixar topic-tailored storybook canvas
    if base_img is None:
        base_img = Image.new("RGB", (width, height), "#0F172A")
        draw_grad = ImageDraw.Draw(base_img)
        topic_lower = (topic or title or "").lower()

        # Sky gradient: vibrant cerulean to sunny turquoise
        for y in range(height):
            ratio = y / height
            r = int(40 * (1 - ratio) + 14 * ratio)
            g = int(180 * (1 - ratio) + 165 * ratio)
            b = int(250 * (1 - ratio) + 233 * ratio)
            draw_grad.line([(0, y), (width, y)], fill=(r, g, b))

        # Rainbow arc across sky
        rainbow_colors = ["#EF4444", "#F97316", "#FACC15", "#22C55E", "#3B82F6", "#A855F7"]
        center_x, center_y = int(width * 0.72), int(height * 0.52)
        for idx, col in enumerate(rainbow_colors):
            rad = int(width * 0.44) - idx * 12
            draw_grad.arc(
                [center_x - rad, center_y - rad, center_x + rad, center_y + rad],
                start=160,
                end=320,
                fill=col,
                width=14,
            )

        # Smiling cartoon sun in top right
        sun_x, sun_y = int(width * 0.84), int(height * 0.16)
        sun_r = int(height * 0.11)
        draw_grad.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill="#FDE047", outline="#F59E0B", width=5)
        for angle in range(0, 360, 45):
            rad_ang = math.radians(angle)
            x1 = sun_x + int((sun_r + 3) * math.cos(rad_ang))
            y1 = sun_y + int((sun_r + 3) * math.sin(rad_ang))
            x2 = sun_x + int((sun_r + 18) * math.cos(rad_ang))
            y2 = sun_y + int((sun_r + 18) * math.sin(rad_ang))
            draw_grad.line([(x1, y1), (x2, y2)], fill="#F59E0B", width=5)

        # Fluffy white cartoon clouds
        cloud_color = "#FFFFFF"
        for cx_rel, cy_rel, cr_rel in [(0.2, 0.22, 0.08), (0.26, 0.20, 0.10), (0.33, 0.22, 0.08)]:
            ccx, ccy, ccr = int(width * cx_rel), int(height * cy_rel), int(height * cr_rel)
            draw_grad.ellipse([ccx - ccr, ccy - ccr, ccx + ccr, ccy + ccr], fill=cloud_color)

        # Lush rolling preschool hills
        draw_grad.ellipse([int(width * -0.1), int(height * 0.60), int(width * 0.58), int(height * 1.35)], fill="#15803D", outline="#166534", width=6)
        draw_grad.ellipse([int(width * 0.42), int(height * 0.66), int(width * 1.15), int(height * 1.38)], fill="#16A34A", outline="#15803D", width=6)
        draw_grad.ellipse([int(width * 0.12), int(height * 0.74), int(width * 0.88), int(height * 1.42)], fill="#22C55E", outline="#16A34A", width=6)

        # If vehicle / bus topic: Draw winding sunny road
        if "bus" in topic_lower or "wheel" in topic_lower or "car" in topic_lower or "ride" in topic_lower:
            draw_grad.ellipse([int(width * 0.05), int(height * 0.78), int(width * 0.95), int(height * 1.45)], fill="#334155", outline="#64748B", width=6)
            # Dashed yellow road centerline
            for dash_x in range(int(width * 0.15), int(width * 0.85), int(width * 0.06)):
                draw_grad.line([(dash_x, int(height * 0.88)), (dash_x + int(width * 0.03), int(height * 0.88))], fill="#FACC15", width=5)

    # 4. Pixar 3D Bubble Typography Overlay (Compact & High-CTR)
    draw = ImageDraw.Draw(base_img, "RGBA")

    # Short, punchy headline (1 to 2 words max)
    short_title = extract_short_thumbnail_title(title, topic)
    words = short_title.split()
    if len(words) >= 3:
        line1 = " ".join(words[:2])
        line2 = " ".join(words[2:])
    else:
        line1 = short_title
        line2 = ""

    # Helper to draw compact 3D Pixar Bubble Text with vibrant multi-layer effects
    def draw_3d_bubble(
        text: str,
        cx: int,
        cy: int,
        font,
        fill_color="#00D4FF",
        gradient_bottom="#0077FF",
        inner_stroke="#004499",
        border_color="#FFFFFF",
        border_radius=8,
        shadow_offset=(4, 5),
        shadow_color=(0, 15, 45, 220),
        add_sparkles=True,
    ):
        if not text:
            return
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = cx - tw // 2
        ty = cy - th // 2

        # 1. Deep 3D Extruded Drop Shadow
        sox, soy = shadow_offset
        for s_step in range(soy, 0, -1):
            draw.text((tx + sox, ty + s_step), text, fill=shadow_color, font=font)

        # 2. Sleek Rounded White Puffy Casing
        for r in range(border_radius, 0, -2):
            for angle in range(0, 360, 20):
                rad = math.radians(angle)
                ox = int(r * math.cos(rad))
                oy = int(r * math.sin(rad))
                draw.text((tx + ox, ty + oy), text, fill=border_color, font=font)

        # 3. Inner Contrast Stroke
        for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 2), (0, -2), (2, 0), (-2, 0)]:
            draw.text((tx + ox, ty + oy), text, fill=inner_stroke, font=font)

        # 4. Bottom Depth Tone
        draw.text((tx, ty + 2), text, fill=gradient_bottom, font=font)

        # 5. Main Vibrant Candy Fill
        draw.text((tx, ty), text, fill=fill_color, font=font)

        # 6. Top Glossy Specular Arc Reflection
        draw.text((tx - 1, ty - 1), text, fill="#FFFFFF", font=font)
        draw.text((tx, ty - 1), text, fill="#E0F7FF", font=font)

        # 7. Decorative 3D Sparkle Stars around text
        if add_sparkles:
            sparkle_font = _get_best_font(size=int(font.size * 0.4), bold=True)
            draw.text((tx - 18, ty - 10), "✦", fill="#FFF59D", font=sparkle_font)
            draw.text((tx + tw + 4, ty - 8), "✦", fill="#FFF59D", font=sparkle_font)

    # Compact Headline Font Sizing (Does NOT overpower artwork)
    title_size = 46 if not is_vertical else 54
    if len(line1) <= 8 and not line2:
        title_size = 50 if not is_vertical else 58

    title_font = _get_best_font(size=title_size, bold=True)
    title_center_x = width // 2

    if line2:
        draw_3d_bubble(
            line1, title_center_x, int(height * 0.12), title_font,
            fill_color="#00E5FF", gradient_bottom="#0080FF", inner_stroke="#003D82",
            border_radius=8, add_sparkles=True,
        )
        draw_3d_bubble(
            line2, title_center_x, int(height * 0.22), title_font,
            fill_color="#FFE600", gradient_bottom="#FF8800", inner_stroke="#B34700",
            border_radius=8, shadow_color=(40, 10, 0, 220), add_sparkles=True,
        )
    else:
        draw_3d_bubble(
            line1, title_center_x, int(height * 0.14), title_font,
            fill_color="#00E5FF", gradient_bottom="#0080FF", inner_stroke="#003D82",
            border_radius=8, add_sparkles=True,
        )

    # 5. Bottom Subtitle Compact 3D Pill Badge
    clean_topic = topic.split(":")[0].split("|")[0].strip() if topic else "Preschool Song"
    if clean_topic.lower() in ("preschool song", "nursery rhymes", "kids song"):
        subtitle_text = "Fun Kids Song 🎶"
    else:
        subtitle_text = f"{clean_topic[:26]} 🎶"

    badge_font_size = 24 if not is_vertical else 28
    badge_font = _get_best_font(size=badge_font_size, bold=True)
    sub_cy = int(height * 0.92) if not is_vertical else int(height * 0.95)
    sub_cx = width // 2

    # Draw Compact Golden Pill Badge
    def draw_golden_pill_badge(text: str, cx: int, cy: int, font):
        full_text = f"✨  {text}  ✨"
        bbox = draw.textbbox((0, 0), full_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        pad_x, pad_y = 18, 6
        rx0, ry0 = cx - tw // 2 - pad_x, cy - th // 2 - pad_y
        rx1, ry1 = cx + tw // 2 + pad_x, cy + th // 2 + pad_y
        radius = (ry1 - ry0) // 2

        # 1. Pill Drop Shadow
        draw.rounded_rectangle([rx0 + 2, ry0 + 4, rx1 + 2, ry1 + 4], radius=radius, fill=(0, 0, 0, 150))
        # 2. Outer White Stroke
        draw.rounded_rectangle([rx0 - 2, ry0 - 2, rx1 + 2, ry1 + 2], radius=radius + 2, fill="#FFFFFF")
        # 3. Main Gradient Fill
        draw.rounded_rectangle([rx0, ry0, rx1, ry1], radius=radius, fill="#FFB300", outline="#E65100", width=2)
        # 4. Top Highlight
        draw.rounded_rectangle([rx0 + 3, ry0 + 2, rx1 - 3, ry0 + (ry1 - ry0) // 2], radius=radius // 2, fill="#FFE082")
        # 5. Text
        tx = cx - tw // 2
        ty = cy - th // 2
        draw.text((tx + 1, ty + 1), full_text, fill=(80, 20, 0, 200), font=font)
        draw.text((tx, ty), full_text, fill="#1A1A1A", font=font)

    draw_golden_pill_badge(subtitle_text, sub_cx, sub_cy, badge_font)

    # 6. Save final high-CTR thumbnail JPEG
    base_img = base_img.convert("RGB")
    base_img.save(output_thumbnail_path, format="JPEG", quality=96, optimize=True)
    return output_thumbnail_path
