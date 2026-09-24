import os
import json
import logging
import urllib.request
import subprocess
import shutil
from typing import Dict, Any, List, Optional

logger = logging.getLogger("studio.suno")


def format_suno_prompt(topic: str, lyrics_lines: List[str]) -> Dict[str, str]:
    """
    Formats preschool nursery rhyme into Suno.ai prompt format with song structure tags.
    """
    clean_topic = topic.strip().capitalize()
    
    # Suno tags
    prompt_text = f"[Genre: Preschool Children Pop, Catchy Preschool Pop Style]\n[Tempo: 120 BPM, Bright Melodic]\n[Instruments: Glockenspiel, Acoustic Guitar, Warm Bass, Cheerful Clap]\n\n"
    
    if lyrics_lines:
        chunk_size = max(1, len(lyrics_lines) // 4)
        v1 = "\n".join(lyrics_lines[:chunk_size])
        ch = "\n".join(lyrics_lines[chunk_size:chunk_size*2]) or f"Singing together about {clean_topic}!\nHappy all the whole day long!"
        v2 = "\n".join(lyrics_lines[chunk_size*2:chunk_size*3]) or "Clap your hands and spin around,\nHear the lovely cheerful sound!"
        outro = "\n".join(lyrics_lines[chunk_size*3:]) or "Wave goodbye with smiling eyes,\nUnder sunny rainbow skies!"

        prompt_text += f"[Verse 1]\n{v1}\n\n[Chorus]\n{ch}\n\n[Verse 2]\n{v2}\n\n[Outro]\n{outro}\n[End]"
    else:
        prompt_text += f"[Verse]\nLet's all sing about {clean_topic} today,\nDancing and playing in a sunny way!\n\n[Chorus]\nHappy smiles for everyone,\nLearning together in the sun!\n[End]"

    style_tags = f"preschool, nursery rhyme, kids singalong, glockenspiel, acoustic, upbeat, cute vocals, {clean_topic.lower()}"

    return {
        "title": f"The {clean_topic} Song",
        "prompt": prompt_text,
        "tags": style_tags,
        "make_instrumental": False,
    }


def generate_suno_track(
    topic: str,
    lyrics_lines: List[str],
    output_wav: str,
    duration_sec: float = 60.0,
) -> Optional[str]:
    """
    Calls external Suno API if configured via SUNO_API_KEY / SUNO_API_URL.
    Returns path to downloaded audio file or None if unconfigured/offline.
    """
    api_key = os.environ.get("SUNO_API_KEY", "").strip()
    api_url = os.environ.get("SUNO_API_URL", "").strip()

    if not api_key and not api_url:
        logger.info("Suno.ai API key not configured; using local neural chime orchestrator.")
        return None

    target_url = api_url or "https://api.suno.ai/v1/generate"
    payload = format_suno_prompt(topic, lyrics_lines)

    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(
            target_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status in (200, 201):
                res_json = json.loads(response.read().decode("utf-8"))
                audio_url = res_json.get("audio_url") or res_json.get("url")
                if audio_url:
                    temp_mp3 = output_wav.replace(".wav", "_suno.mp3")
                    urllib.request.urlretrieve(audio_url, temp_mp3)

                    # Convert to standard 44.1kHz stereo WAV via FFmpeg
                    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
                    subprocess.run(
                        [ffmpeg_bin, "-y", "-i", temp_mp3, "-ar", "44100", "-ac", "2", output_wav],
                        check=True,
                    )
                    if os.path.exists(temp_mp3):
                        os.remove(temp_mp3)
                    return output_wav
    except Exception as e:
        logger.warning(f"Suno AI API generation bypassed: {e}")
        return None

    return None
