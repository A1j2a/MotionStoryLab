import os
import sys
import json
import shutil
import subprocess
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("studio.blender")


def get_blender_binary() -> Optional[str]:
    """Finds Blender 4.x/5.x executable on macOS/Linux."""
    candidates = [
        shutil.which("blender"),
        "/opt/homebrew/bin/blender",
        "/usr/local/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
    ]
    for c in candidates:
        if c and os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None


def render_blender_3d_scene(
    scene_number: int,
    topic: str,
    verse_text: str,
    duration_sec: float,
    output_mp4: str,
    character_info: Optional[Dict[str, Any]] = None,
    environment_name: Optional[str] = None,
    camera_style: Optional[Dict[str, Any]] = None,
    width: int = 1280,
    height: int = 720,
    fps: int = 24,
) -> bool:
    """
    Executes Headless Blender 5.2 with Metal GPU acceleration to render state-of-the-art
    3D preschool animation scenes (Buster Bus, Twinkle Star, Daisy Cow, Happy Apple, Toto Train).
    """
    blender_bin = get_blender_binary()
    if not blender_bin:
        logger.info("Blender executable not found in standard paths.")
        return False

    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "blender",
        "render_scene.py",
    )
    if not os.path.exists(script_path):
        logger.warning(f"Blender script not found at {script_path}")
        return False

    out_dir = os.path.dirname(os.path.abspath(output_mp4))
    os.makedirs(out_dir, exist_ok=True)
    temp_json = os.path.join(out_dir, f"blender_scene_{scene_number}.json")

    scene_data = {
        "scene_number": scene_number,
        "topic": topic,
        "verse_text": verse_text,
        "environment": environment_name or "preschool",
        "duration": float(duration_sec),
        "fps": int(fps),
        "res_x": int(width),
        "res_y": int(height),
        "output_path": output_mp4,
        "character": character_info or {},
        "camera": camera_style or {},
    }

    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump(scene_data, f, indent=2)

    cmd = [
        blender_bin,
        "-b",
        "-P", script_path,
        "--", temp_json,
    ]

    try:
        logger.info(f"Rendering 3D Scene {scene_number} via Blender 5.2 Metal GPU...")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if os.path.exists(temp_json):
            os.remove(temp_json)

        if res.returncode == 0 and os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 5000:
            logger.info(f"Blender 3D Scene {scene_number} rendered successfully: {output_mp4}")
            return True
        else:
            logger.warning(f"Blender render returned {res.returncode}: {res.stderr[:200]}")
    except Exception as e:
        logger.warning(f"Blender execution exception: {e}")

    return False
