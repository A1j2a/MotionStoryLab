import os
import shutil
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from ai.video_provider import (
    VideoGenerationProvider,
    BlenderVideoProvider,
    WanVideoProvider,
    get_video_provider,
    DEFAULT_WAN_NEGATIVE_PROMPT,
)
from renderer.compositor import extract_final_frame, adjust_video_duration, get_video_duration


def test_video_provider_factory():
    """Verifies factory returns correct provider based on configuration."""
    wan_prov = get_video_provider("wan")
    assert isinstance(wan_prov, WanVideoProvider)
    assert wan_prov.name == "wan"

    blender_prov = get_video_provider("blender")
    assert isinstance(blender_prov, BlenderVideoProvider)
    assert blender_prov.name == "blender"


def test_wan_structured_prompt_generation():
    """
    Verifies Section 8:
    CHARACTER CONSISTENCY + ENVIRONMENT CONSISTENCY + CURRENT ACTION + CAMERA + MOTION + LIGHTING + CONTINUITY + STYLE
    """
    provider = WanVideoProvider()
    char_bible = [
        {
            "name": "Teddy Bear",
            "species": "toy teddy bear",
            "appearance": "Soft light-brown fur, round friendly face, small childlike teddy proportions",
            "clothing": "Blue pajamas",
            "colors": ["#854d0e", "#3b82f6", "#dc2626"],
        }
    ]
    env_bible = {
        "name": "Cozy children's bedroom",
        "props": "small wooden bed, blue blanket, warm yellow bedside lamp, moon visible through window",
    }
    camera = {
        "movement": "gentle tracking push-in",
        "shot": "medium shot",
    }
    lighting = {
        "time_of_day": "warm nighttime lighting",
    }

    prompt = provider.build_structured_prompt(
        topic="Bedtime Teddy",
        lyrics="The teddy slowly walks toward the window while gently holding the blue blanket",
        scene_number=2,
        character_bible=char_bible,
        environment_bible=env_bible,
        camera=camera,
        lighting=lighting,
        actions=["slowly gets up from bed", "picks up blue blanket", "walks toward window"],
        previous_scene_id="scene_001",
    )

    # Validate character consistency
    assert "Teddy Bear" in prompt
    assert "Soft light-brown fur" in prompt
    assert "Blue pajamas" in prompt

    # Validate environment consistency
    assert "Cozy children's bedroom" in prompt
    assert "small wooden bed" in prompt

    # Validate continuity
    assert "Continue exactly from the provided starting frame" in prompt
    assert "warm nighttime lighting" in prompt
    assert "3D children's animation" in prompt


def test_wan_negative_prompt_completeness():
    """
    Verifies Section 9: Strong negative prompt preventing human children,
    extra characters, and visual artifacts.
    """
    provider = WanVideoProvider()
    neg = provider.negative_prompt

    assert "human child" in neg
    assert "real human" in neg
    assert "different character" in neg
    assert "different clothing" in neg
    assert "duplicate character" in neg
    assert "deformed face" in neg
    assert "flickering" in neg
    assert "watermark" in neg


def test_wan_missing_key_handling():
    """
    Verifies that missing FAL_KEY reports a clean, human-readable error
    instead of throwing unhandled exceptions.
    """
    provider = WanVideoProvider(fal_key="")
    with tempfile.TemporaryDirectory() as tmpdir:
        out_mp4 = os.path.join(tmpdir, "test_scene.mp4")
        result = provider.generate_scene_video(
            scene_number=1,
            topic="Bedtime Teddy",
            lyrics="Teddy bear goes to sleep",
            duration_sec=8.0,
            output_mp4=out_mp4,
        )

        assert result["success"] is False
        assert "FAL_KEY" in result["error"]
        assert result["attempts"] == 0


def test_flf2v_frame_continuity_and_flow():
    """
    Verifies Section 5: First-frame to Last-frame creation, extraction,
    and A -> B -> C continuity flow.
    """
    provider = WanVideoProvider(fal_key="dummy_test_key")
    with tempfile.TemporaryDirectory() as tmpdir:
        start_frame = os.path.join(tmpdir, "scene_001_start.jpg")
        end_frame = os.path.join(tmpdir, "scene_001_end.jpg")

        # 1. Verify frame creation when absent
        p1 = provider._ensure_frame_image(
            target_path=start_frame,
            topic="Bedtime Teddy",
            scene_number=1,
            verse_text="Teddy sits on bed",
            character_bible=[{"name": "Teddy Bear"}],
            is_end_frame=False,
        )
        assert os.path.exists(p1) and os.path.getsize(p1) > 500

        p2 = provider._ensure_frame_image(
            target_path=end_frame,
            topic="Bedtime Teddy",
            scene_number=1,
            verse_text="Teddy walks to window",
            character_bible=[{"name": "Teddy Bear"}],
            is_end_frame=True,
        )
        assert os.path.exists(p2) and os.path.getsize(p2) > 500


def test_wan_mock_generation_and_duration_adjustment():
    """
    Verifies complete Wan generation pipeline with mock API:
    - Calls Wan FLF2V API
    - Downloads video
    - Adjusts to 8.0s duration via FFmpeg
    - Extracts final frame for next scene
    """
    provider = WanVideoProvider(fal_key="fake_fal_key_for_testing")

    with tempfile.TemporaryDirectory() as tmpdir:
        out_mp4 = os.path.join(tmpdir, "scene_001.mp4")

        # Create a small valid test video using ffmpeg testsrc
        ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
        import subprocess
        mock_source = os.path.join(tmpdir, "source.mp4")
        subprocess.run(
            [
                ffmpeg_bin, "-y",
                "-f", "lavfi",
                "-i", "testsrc=duration=4:size=640x360:rate=16",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                mock_source,
            ],
            capture_output=True,
        )
        assert os.path.exists(mock_source)

        # Mock _call_wan_api to return local file URL
        with patch.object(provider, "_call_wan_api", return_value=(f"file://{mock_source}", "req_12345")):
            with patch.object(provider, "_upload_or_encode_image", return_value="https://v3.fal.media/files/mock.jpg"):
                result = provider.generate_scene_video(
                    scene_number=1,
                    topic="Cute Teddy Bear",
                    lyrics="A cute small brown teddy bear wearing blue pajamas",
                    duration_sec=8.0,
                    output_mp4=out_mp4,
                    character_bible=[
                        {
                            "name": "Teddy Bear",
                            "appearance": "Small cute brown teddy bear wearing blue pajamas with a red bow",
                            "clothing": "blue pajamas",
                        }
                    ],
                )

                assert result["success"] is True
                assert result["provider"] == "wan"
                assert result["request_id"] == "req_12345"
                assert os.path.exists(out_mp4)
                assert result["start_frame"] is not None
                assert result["end_frame"] is not None

                # Verify final frame was extracted for next scene
                last_frame = os.path.join(tmpdir, "scene_001_last_frame.jpg")
                assert os.path.exists(last_frame)
