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


def generate_high_ctr_thumbnail(
    title: str = "Kids Nursery Rhyme",
    topic: str = "Preschool Song",
    output_thumbnail_path: str = "thumbnail.jpg",
    video_path: Optional[str] = None,
    aspect_ratio: str = "16:9",
    character_name: str = "Hero",
) -> str:
    """
    Generates an ultra-high CTR / high-CPM YouTube Kids thumbnail.
    Combines video frame (or vibrant 3D Pixar gradient), bold multi-layer 3D typography,
    eye-catching badges ('NEW EPISODE', 'SING ALONG'), and saturated nursery color palette.
    Supports 16:9 (1280x720) and 9:16 (1080x1920).
    """
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

    os.makedirs(os.path.dirname(os.path.abspath(output_thumbnail_path)), exist_ok=True)
    is_vertical = (aspect_ratio == "9:16")
    width, height = (1080, 1920) if is_vertical else (1280, 720)

    # 1. Base Image: Try extracting frame from video if present
    base_img = None
    if video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 1000:
        temp_frame = output_thumbnail_path + ".raw.jpg"
        try:
            generate_thumbnail(video_path, temp_frame)
            if os.path.exists(temp_frame) and os.path.getsize(temp_frame) > 1000:
                raw_im = Image.open(temp_frame).convert("RGB")
                base_img = raw_im.resize((width, height), Image.Resampling.LANCZOS)
                # Boost saturation & contrast for High-CTR YouTube Kids standard
                enhancer = ImageEnhance.Color(base_img)
                base_img = enhancer.enhance(1.35)
                bright_enh = ImageEnhance.Brightness(base_img)
                base_img = bright_enh.enhance(1.08)
                os.remove(temp_frame)
        except Exception:
            pass

    # 2. If no video frame, create vibrant Pixar sunset / rainbow gradient canvas
    if base_img is None:
        base_img = Image.new("RGB", (width, height), "#1E1B4B")
        draw_grad = ImageDraw.Draw(base_img)
        for y in range(height):
            ratio = y / height
            r = int(255 * (1 - ratio * 0.4))
            g = int(140 * (1 - ratio * 0.3) + 70 * ratio)
            b = int(50 * (1 - ratio) + 220 * ratio)
            draw_grad.line([(0, y), (width, y)], fill=(r, g, b))

        # Add decorative bright playful circles
        draw_grad.ellipse([int(width * 0.7), int(height * 0.05), int(width * 0.98), int(height * 0.45)], fill="#FDE047", outline="#F59E0B", width=8)
        draw_grad.ellipse([int(width * 0.05), int(height * 0.6), int(width * 0.45), int(height * 1.1)], fill="#10B981", outline="#059669", width=8)
        draw_grad.ellipse([int(width * 0.4), int(height * 0.7), int(width * 0.95), int(height * 1.2)], fill="#3B82F6", outline="#2563EB", width=8)

    draw = ImageDraw.Draw(base_img, "RGBA")

    # 3. High-CTR Glowing Vignette Border
    border_w = 16 if not is_vertical else 24
    for i in range(border_w):
        alpha = int(220 * (1 - i / border_w))
        draw.rectangle([i, i, width - i, height - i], outline=(255, 220, 0, alpha), width=1)

    # 4. Top-Left High-CPM Badge ('★ POPULAR KIDS SONG ★' or '🔥 NEW EPISODE')
    badge_w = 340 if not is_vertical else 420
    badge_h = 56 if not is_vertical else 72
    badge_x = 36
    badge_y = 36
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=18, fill=(239, 68, 68, 245), outline=(255, 255, 255, 255), width=4)

    # Text overlay
    badge_text = "🔥 NEW PRESCHOOL HIT!"
    draw.text((badge_x + 24, badge_y + 12), badge_text, fill="#FFFFFF")

    # Top-Right Badge ('4K ULTRA HD')
    tr_w = 180 if not is_vertical else 220
    tr_x = width - tr_w - 36
    draw.rounded_rectangle([tr_x, badge_y, tr_x + tr_w, badge_y + badge_h], radius=18, fill=(37, 99, 235, 245), outline=(255, 255, 255, 255), width=4)
    draw.text((tr_x + 28, badge_y + 12), "⭐ 4K KIDS", fill="#FFFFFF")

    # 5. Bold 3D Multi-Layered Title Banner (Bottom Hook for High Click-Through Rate)
    clean_title = title.split(":")[0].strip() if ":" in title else title.strip()
    if len(clean_title) > 32:
        clean_title = clean_title[:30] + "..."

    banner_h = int(height * 0.28)
    banner_y = height - banner_h - 28
    banner_x1 = 28
    banner_x2 = width - 28

    # Dark translucent backdrop for maximum text readability
    draw.rounded_rectangle([banner_x1, banner_y, banner_x2, banner_y + banner_h], radius=24, fill=(15, 23, 42, 215), outline=(250, 204, 21, 255), width=6)

    # Draw Title with 3D drop shadow effect
    text_x = banner_x1 + 32
    text_y = banner_y + 24

    # Subtitle hook
    hook_text = f"Sing Along with {character_name}! 🎈"
    draw.text((text_x, text_y), hook_text, fill="#38BDF8")

    # Main Headline in Big 3D Yellow / White
    headline = clean_title.upper()
    for offset_x, offset_y in [(4, 4), (3, 3), (2, 2), (-2, -2), (2, -2), (-2, 2)]:
        draw.text((text_x + offset_x, text_y + 42 + offset_y), headline, fill="#000000")

    draw.text((text_x, text_y + 42), headline, fill="#FDE047")

    # Save final thumbnail JPEG
    base_img = base_img.convert("RGB")
    base_img.save(output_thumbnail_path, format="JPEG", quality=94, optimize=True)
    return output_thumbnail_path
