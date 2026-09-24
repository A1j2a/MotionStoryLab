import os
import shutil
import subprocess
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from audio.suno_adapter import generate_suno_track
from audio.synthesizer import generate_nursery_melody, synthesize_vocals, mix_soundtrack

logger = logging.getLogger("studio.audio.providers")


class BaseMusicProvider(ABC):
    """Abstract base class for Song/Music generation providers."""

    @abstractmethod
    def generate_song(
        self,
        approved_lyrics: str,
        music_style: str,
        voice_style: str,
        duration_sec: float,
        output_path: str,
        topic: str = "",
    ) -> str:
        """Generates full song audio file from exact approved lyrics."""
        pass


class SunoMusicProvider(BaseMusicProvider):
    """Suno AI Music Generation Provider (Cloud / Local Proxy)."""

    def generate_song(
        self,
        approved_lyrics: str,
        music_style: str,
        voice_style: str,
        duration_sec: float,
        output_path: str,
        topic: str = "",
    ) -> str:
        lyrics_lines = [l.strip() for l in approved_lyrics.splitlines() if l.strip() and not l.startswith("[")]
        suno_file = generate_suno_track(
            topic=topic or "Preschool Song",
            lyrics_lines=lyrics_lines,
            output_wav=output_path,
            duration_sec=duration_sec,
        )
        if suno_file and os.path.exists(suno_file):
            return suno_file

        logger.info("Suno generation unavailable or unconfigured, falling back to LocalMusicProvider.")
        local_prov = LocalMusicProvider()
        return local_prov.generate_song(approved_lyrics, music_style, voice_style, duration_sec, output_path, topic)


class LocalMusicProvider(BaseMusicProvider):
    """
    Local multi-track preschool music engine.
    Synthesizes rich nursery backing melody, vocals via voice provider, and mixes master soundtrack.
    100% offline, zero API fees.
    """

    def generate_song(
        self,
        approved_lyrics: str,
        music_style: str,
        voice_style: str,
        duration_sec: float,
        output_path: str,
        topic: str = "",
    ) -> str:
        lyrics_lines = [l.strip() for l in approved_lyrics.splitlines() if l.strip() and not l.startswith("[")]
        out_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(out_dir, exist_ok=True)

        music_tmp = os.path.join(out_dir, "music_backing.wav")
        vocals_tmp = os.path.join(out_dir, "vocals_track.wav")

        # 1. Backing melody
        generate_nursery_melody(
            music_tmp,
            duration_sec=duration_sec,
            tempo_bpm=120,
            topic=topic,
            lyrics_lines=lyrics_lines,
        )

        # 2. Vocal narration / singing
        voice_prov = get_voice_provider()
        voice_prov.synthesize_voice(
            text=". ".join(lyrics_lines),
            voice_style=voice_style,
            output_path=vocals_tmp,
            duration_sec=duration_sec,
        )

        # 3. Mix master soundtrack
        mixed = mix_soundtrack(music_tmp, vocals_tmp, output_path)
        return mixed


class BaseVoiceProvider(ABC):
    """Abstract base class for TTS / Voice providers."""

    @abstractmethod
    def synthesize_voice(self, text: str, voice_style: str, output_path: str, duration_sec: float = 60.0) -> str:
        pass


class KokoroVoiceProvider(BaseVoiceProvider):
    """Kokoro Neural TTS Provider (Port 8880)."""

    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = (endpoint or os.environ.get("KOKORO_TTS_URL", "http://127.0.0.1:8880")).rstrip("/")

    def synthesize_voice(self, text: str, voice_style: str, output_path: str, duration_sec: float = 60.0) -> str:
        import urllib.request
        import json

        url = f"{self.endpoint}/v1/audio/speech"
        payload = {
            "input": text,
            "voice": "af_bella" if "female" in voice_style.lower() or "soprano" in voice_style.lower() else "am_adam",
            "response_format": "wav",
            "speed": 1.0,
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12) as res:
                if res.status == 200:
                    with open(output_path, "wb") as f:
                        f.write(res.read())
                    return output_path
        except Exception as e:
            logger.warning(f"Kokoro TTS call failed, falling back to macOS say: {e}")

        macos_prov = MacosVoiceProvider()
        return macos_prov.synthesize_voice(text, voice_style, output_path, duration_sec)


class MacosVoiceProvider(BaseVoiceProvider):
    """macOS Speech Engine (Samantha/Daniel) with studio vocal polish."""

    def synthesize_voice(self, text: str, voice_style: str, output_path: str, duration_sec: float = 60.0) -> str:
        lyrics_lines = [t.strip() for t in text.split(".") if t.strip()]
        return synthesize_vocals(lyrics_lines, output_path, duration_sec=duration_sec)


def get_music_provider() -> BaseMusicProvider:
    """Factory: returns configured MusicProvider."""
    if os.environ.get("SUNO_API_KEY") or os.environ.get("SUNO_API_URL"):
        return SunoMusicProvider()
    return LocalMusicProvider()


def get_voice_provider() -> BaseVoiceProvider:
    """Factory: returns configured VoiceProvider."""
    if os.environ.get("KOKORO_TTS_URL"):
        return KokoroVoiceProvider()
    return MacosVoiceProvider()
