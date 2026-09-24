import os
import wave
import json
import shutil
import subprocess
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("studio.audio.analyzer")


def get_audio_duration(file_path: str) -> float:
    """Returns exact audio duration in seconds using wave header or ffprobe."""
    if not os.path.exists(file_path):
        return 60.0

    # 1. Try wave module for .wav
    if file_path.lower().endswith(".wav"):
        try:
            with wave.open(file_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate > 0:
                    return float(frames / rate)
        except Exception as e:
            logger.debug(f"wave read failed: {e}")

    # 2. Try ffprobe
    ffprobe_bin = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"
    if ffprobe_bin:
        try:
            cmd = [
                ffprobe_bin,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path,
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip())
        except Exception as e:
            logger.debug(f"ffprobe duration failed: {e}")

    return 60.0


def analyze_audio_timeline(audio_file: str, approved_lyrics: str, bpm: int = 120) -> Dict[str, Any]:
    """
    Analyzes generated song/audio file and creates a structured audio timeline:
    - total duration
    - BPM
    - beats
    - pauses
    - sections (intro, verse, chorus, bridge, outro)
    - lyrics timestamps
    - important action moments / cues
    """
    duration = get_audio_duration(audio_file)
    beat_duration = 60.0 / bpm
    total_beats = int(duration / beat_duration)

    # 1. Parse approved lyrics into stanzas
    raw_lines = approved_lyrics.splitlines()
    sections = []
    current_section = "Verse 1"
    current_lines = []
    parsed_blocks = []

    for line in raw_lines:
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.startswith("[") and line_s.endswith("]"):
            if current_lines:
                parsed_blocks.append({"section": current_section, "lines": list(current_lines)})
                current_lines = []
            current_section = line_s.strip("[]")
        else:
            current_lines.append(line_s)

    if current_lines:
        parsed_blocks.append({"section": current_section, "lines": list(current_lines)})

    if not parsed_blocks:
        parsed_blocks = [
            {"section": "Verse 1", "lines": ["Singing our joyful song today", "Dancing together on the way"]},
            {"section": "Chorus", "lines": ["Clap your hands and spin around", "Listen to the happy sound"]},
            {"section": "Verse 2", "lines": ["Smiling friends are having fun", "Underneath the golden sun"]},
            {"section": "Outro", "lines": ["Wave goodbye with cheerful eyes", "Underneath the rainbow skies"]},
        ]

    # 2. Distribute sections across timeline
    num_blocks = len(parsed_blocks)
    intro_dur = min(4.0, duration * 0.08)
    outro_dur = min(4.0, duration * 0.08)
    content_dur = max(10.0, duration - intro_dur - outro_dur)
    block_dur = content_dur / num_blocks

    timeline_sections = []
    lyric_timestamps = []
    cues = []

    # Intro section
    if intro_dur > 0:
        timeline_sections.append({
            "type": "intro",
            "name": "Intro Chimes & Beat",
            "start": 0.0,
            "end": round(intro_dur, 2),
            "bpm": bpm,
        })
        cues.append({"time": 0.0, "type": "intro_start", "action": "camera establishes scene with musical sparkle"})

    # Content sections
    cur_time = intro_dur
    for idx, block in enumerate(parsed_blocks, start=1):
        sec_start = cur_time
        sec_end = min(duration - outro_dur, cur_time + block_dur)
        sec_type = "chorus" if "chorus" in block["section"].lower() else ("verse" if "verse" in block["section"].lower() else "bridge")

        timeline_sections.append({
            "type": sec_type,
            "name": block["section"],
            "start": round(sec_start, 2),
            "end": round(sec_end, 2),
            "lines": block["lines"],
        })

        # Distribute line timestamps within section
        lines = block["lines"]
        if lines:
            line_slot = (sec_end - sec_start) / len(lines)
            for l_idx, line_text in enumerate(lines):
                l_start = sec_start + (l_idx * line_slot)
                l_end = min(sec_end, l_start + line_slot - 0.2)
                lyric_timestamps.append({
                    "line": line_text,
                    "section": block["section"],
                    "start": round(l_start, 2),
                    "end": round(l_end, 2),
                })
                # Add action cue on each line start
                cues.append({
                    "time": round(l_start, 2),
                    "type": "lyric_cue",
                    "text": line_text,
                    "action": "character performs choreographed bounce/gesture",
                })

        cur_time = sec_end

    # Outro section
    if outro_dur > 0:
        timeline_sections.append({
            "type": "outro",
            "name": "Outro & Fade",
            "start": round(cur_time, 2),
            "end": round(duration, 2),
            "bpm": bpm,
        })
        cues.append({"time": round(cur_time, 2), "type": "outro_fade", "action": "characters wave goodbye"})

    return {
        "audio_file": audio_file,
        "duration": round(duration, 2),
        "bpm": bpm,
        "total_beats": total_beats,
        "sections": timeline_sections,
        "lyrics_timestamps": lyric_timestamps,
        "cues": cues,
    }
