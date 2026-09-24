import os
import math
import shutil
import subprocess
from typing import List, Optional


def get_ffmpeg_path() -> str:
    return shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"


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
