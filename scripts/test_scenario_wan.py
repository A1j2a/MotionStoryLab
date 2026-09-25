#!/usr/bin/env python3
"""
Test Scenario Verification for Wan Video Provider (Section 18).
Scene: A cute small brown teddy bear wearing blue pajamas with a red bow sitting on a bed
in a cozy children's bedroom at night, gets up, picks up blue blanket and walks toward window.
"""

import os
import sys
from pathlib import Path

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ai.video_provider import WanVideoProvider, get_video_provider
from renderer.compositor import extract_final_frame, get_video_duration


def run_teddy_bear_scenario():
    print("=" * 60)
    print("RUNNING SECTION 18 TEST SCENARIO: TEDDY BEAR WAN FLF2V")
    print("=" * 60)

    provider = get_video_provider("wan")
    assert isinstance(provider, WanVideoProvider)

    # 1. Define Character Bible (Teddy Bear)
    character_bible = [
        {
            "name": "Teddy Bear",
            "species": "teddy bear",
            "appearance": "Small cute brown teddy bear with soft light-brown fur, round friendly face, and small childlike teddy proportions",
            "clothing": "Blue pajamas with a small red bow",
            "colors": ["#854d0e", "#3b82f6", "#ef4444"],
        }
    ]

    # 2. Define Environment Bible (Cozy Children's Bedroom)
    environment_bible = {
        "name": "Cozy children's bedroom",
        "props": "small wooden bed, blue blanket, warm yellow bedside lamp, moon visible through window",
    }

    camera = {
        "movement": "gentle slow tracking pan from bed toward window",
        "shot": "medium full shot",
    }
    lighting = {
        "time_of_day": "warm nighttime lighting with moonlight rim light",
    }
    actions = [
        "is sitting on a bed in a cozy bedroom at night",
        "slowly gets up",
        "picks up a blue blanket",
        "walks toward the window while gently holding the blue blanket",
    ]

    # 3. Generate structured prompt
    prompt = provider.build_structured_prompt(
        topic="Teddy Bear Nighttime Journey",
        lyrics="The teddy slowly gets up, picks up a blue blanket and walks toward the window",
        scene_number=1,
        character_bible=character_bible,
        environment_bible=environment_bible,
        camera=camera,
        lighting=lighting,
        actions=actions,
    )

    print("\n[1] Structured Prompt Built:")
    print(f"    {prompt}\n")

    print("[2] Negative Prompt Applied:")
    print(f"    {provider.negative_prompt}\n")

    # 4. Check FAL_KEY
    fal_key = provider.fal_key or os.environ.get("FAL_KEY", "")
    output_dir = ROOT_DIR / "projects" / "test_wan_output"
    os.makedirs(output_dir, exist_ok=True)
    output_mp4 = str(output_dir / "scene_001_teddy.mp4")

    if not fal_key:
        print("[3] NOTICE: FAL_KEY is not configured yet in .env or Settings.")
        print("    To run live generation on Fal.ai, set FAL_KEY=... in .env or in the Settings UI.")
        print("    Demonstrating frame continuity creation & validation locally...")

        # Create start frame & end frame
        start_frame = str(output_dir / "scene_001_teddy_start.jpg")
        end_frame = str(output_dir / "scene_001_teddy_end.jpg")

        provider._ensure_frame_image(
            target_path=start_frame,
            topic="Cute Teddy Bear",
            scene_number=1,
            verse_text="Teddy Bear sitting on bed in blue pajamas",
            character_bible=character_bible,
            is_end_frame=False,
        )
        provider._ensure_frame_image(
            target_path=end_frame,
            topic="Cute Teddy Bear",
            scene_number=1,
            verse_text="Teddy Bear at window with blanket",
            character_bible=character_bible,
            is_end_frame=True,
        )

        print(f"    ✓ Start Frame Generated: {start_frame} ({os.path.getsize(start_frame)} bytes)")
        print(f"    ✓ End Frame Generated:   {end_frame} ({os.path.getsize(end_frame)} bytes)")
        print("\n[4] Scenario setup verified successfully! Ready for live FAL_KEY.")
        return True

    print("[3] Executing live Wan FLF2V generation with configured FAL_KEY...")
    res = provider.generate_scene_video(
        scene_number=1,
        topic="Teddy Bear Nighttime Journey",
        lyrics="The teddy slowly gets up, picks up a blue blanket and walks toward the window",
        duration_sec=8.0,
        output_mp4=output_mp4,
        character_bible=character_bible,
        environment_bible=environment_bible,
        camera=camera,
        lighting=lighting,
        actions=actions,
    )

    if res["success"]:
        print(f"    ✓ Scene 1 Video Generated: {output_mp4}")
        print(f"    ✓ Provider Request ID: {res.get('request_id')}")
        print(f"    ✓ Video URL: {res.get('video_url')}")
        dur = get_video_duration(output_mp4)
        print(f"    ✓ Output Video Duration: {dur:.2f} seconds")

        # Test extraction of final frame for Scene 2 start frame
        next_start = str(output_dir / "scene_002_start_from_scene_001.jpg")
        extract_final_frame(output_mp4, next_start)
        print(f"    ✓ Continuity Frame Extracted for Scene 2: {next_start}")
        print("\nSCENARIO TEST COMPLETED SUCCESSFULLY!")
        return True
    else:
        print(f"    ✗ Generation failed: {res.get('error')}")
        return False


if __name__ == "__main__":
    success = run_teddy_bear_scenario()
    sys.exit(0 if success else 1)
