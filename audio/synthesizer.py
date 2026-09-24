import os
import re
import math
import struct
import wave
import shutil
import subprocess
import random
from typing import Dict, Any, List, Optional
from audio.suno_adapter import generate_suno_track


def generate_nursery_melody(
    output_path: str,
    duration_sec: float = 60.0,
    tempo_bpm: int = 120,
    topic: str = "",
    lyrics_lines: Optional[List[str]] = None,
):
    """
    Generates a rich, multi-layered preschool nursery song backing track:
    - Glockenspiel / marimba chime melody
    - Acoustic piano / warm bell chords (C - Am - F - G progression)
    - Upright walking bassline
    - Bouncy toddler clap-along percussion beat (Kick on 1 & 3, Snare/Clap on 2 & 4)
    - Tries Suno.ai if configured with automatic local fallback
    """
    # 1. Try Suno AI if configured
    if topic and lyrics_lines:
        suno_res = generate_suno_track(topic, lyrics_lines, output_path, duration_sec=duration_sec)
        if suno_res and os.path.exists(output_path):
            return output_path

    sample_rate = 44100
    total_samples = int(duration_sec * sample_rate)
    
    notes = {
        "C2": 65.41, "E2": 82.41, "F2": 87.31, "G2": 98.00, "A2": 110.00, "B2": 123.47,
        "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00, "A3": 220.00, "B3": 246.94,
        "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00, "A4": 440.00, "B4": 493.88,
        "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99, "A5": 880.00,
    }

    # Standard cheerful nursery chord progression (C - Am - F - G)
    chords = [
        ("C3", ["C4", "E4", "G4"]),
        ("A2", ["A3", "C4", "E4"]),
        ("F2", ["F3", "A3", "C4"]),
        ("G2", ["G3", "B3", "D4"]),
    ]

    # Catchy nursery melody theme
    melody_theme = [
        ("C4", 0.5), ("E4", 0.5), ("G4", 0.5), ("G4", 0.5),
        ("A4", 0.5), ("G4", 0.5), ("E4", 1.0),
        ("F4", 0.5), ("A4", 0.5), ("G4", 0.5), ("E4", 0.5),
        ("D4", 0.5), ("E4", 0.5), ("C4", 1.0),
        ("E4", 0.5), ("G4", 0.5), ("C5", 0.5), ("B4", 0.5),
        ("A4", 0.5), ("G4", 0.5), ("E4", 1.0),
        ("F4", 0.5), ("G4", 0.5), ("A4", 0.5), ("B4", 0.5),
        ("C5", 1.5), ("REST", 0.5),
    ]

    beat_dur = 60.0 / tempo_bpm
    raw_left = [0.0] * total_samples
    raw_right = [0.0] * total_samples

    # 1. RHYTHM & DRUMS (Toddler Clap-Along Beat)
    total_beats = int(duration_sec / beat_dur)
    for b in range(total_beats):
        b_time = b * beat_dur
        start_s = int(b_time * sample_rate)
        beat_in_measure = b % 4

        # A) Kick drum on Beats 1 & 3
        if beat_in_measure in (0, 2):
            kick_dur_s = int(0.20 * sample_rate)
            for i in range(kick_dur_s):
                if start_s + i >= total_samples:
                    break
                t = i / sample_rate
                f = 130.0 * math.exp(-22.0 * t) + 45.0
                env = math.exp(-15.0 * t)
                sample = math.sin(2 * math.pi * f * t) * env * 0.55
                raw_left[start_s + i] += sample
                raw_right[start_s + i] += sample

        # B) Crispy Handclap & Snare on Beats 2 & 4
        if beat_in_measure in (1, 3):
            clap_dur_s = int(0.18 * sample_rate)
            for i in range(clap_dur_s):
                if start_s + i >= total_samples:
                    break
                t = i / sample_rate
                # Filtered white noise burst with snap
                noise = (random.random() * 2.0 - 1.0)
                tone = math.sin(2 * math.pi * 320.0 * t)
                env = math.exp(-25.0 * t)
                sample = (0.75 * noise + 0.25 * tone) * env * 0.40
                # Slight stereo width
                raw_left[start_s + i] += sample * 0.95
                raw_right[start_s + i] += sample * 1.05

    # 2. CHORD HARMONIES & BASS (Acoustic Piano & Upright Bass)
    chord_measure_dur = beat_dur * 4.0
    total_measures = int(duration_sec / chord_measure_dur) + 1
    for m in range(total_measures):
        bass_note, chord_notes = chords[m % len(chords)]
        m_start_time = m * chord_measure_dur

        # Bass note at start of measure
        if bass_note in notes:
            bfreq = notes[bass_note]
            bstart_s = int(m_start_time * sample_rate)
            bdur_s = int(beat_dur * 3.5 * sample_rate)
            for i in range(bdur_s):
                if bstart_s + i >= total_samples:
                    break
                t = i / sample_rate
                decay = math.exp(-3.0 * t)
                bsample = (
                    0.65 * math.sin(2 * math.pi * bfreq * t) +
                    0.35 * math.sin(2 * math.pi * (bfreq * 2) * t)
                ) * decay * 0.45
                raw_left[bstart_s + i] += bsample
                raw_right[bstart_s + i] += bsample

        # Piano chords pulsing on each beat
        for b_offset in range(4):
            chord_time = m_start_time + (b_offset * beat_dur)
            cstart_s = int(chord_time * sample_rate)
            cdur_s = int(beat_dur * 0.9 * sample_rate)

            for c_note in chord_notes:
                if c_note in notes:
                    cfreq = notes[c_note]
                    for i in range(cdur_s):
                        if cstart_s + i >= total_samples:
                            break
                        t = i / sample_rate
                        decay = math.exp(-6.0 * t)
                        csample = (
                            0.50 * math.sin(2 * math.pi * cfreq * t) +
                            0.30 * math.sin(2 * math.pi * (cfreq * 2) * t) +
                            0.20 * math.sin(2 * math.pi * (cfreq * 3) * t)
                        ) * decay * 0.15
                        raw_left[cstart_s + i] += csample * 0.85
                        raw_right[cstart_s + i] += csample * 1.15

    # 3. GLOCKENSPIEL / MARIMBA LEAD MELODY
    curr_time = 0.0
    pat_idx = 0
    while curr_time < duration_sec:
        note_name, beats = melody_theme[pat_idx % len(melody_theme)]
        note_dur = beats * beat_dur
        pat_idx += 1

        if note_name != "REST" and note_name in notes:
            freq = notes[note_name]
            start_s = int(curr_time * sample_rate)
            dur_s = int(note_dur * sample_rate)

            for i in range(dur_s):
                if start_s + i >= total_samples:
                    break
                t = i / sample_rate
                # Rich acoustic xylophone envelope
                decay = math.exp(-4.2 * (t / note_dur))
                bell = (
                    0.55 * math.sin(2 * math.pi * freq * t) +
                    0.28 * math.sin(2 * math.pi * (freq * 2) * t) +
                    0.12 * math.sin(2 * math.pi * (freq * 3) * t) +
                    0.05 * math.sin(2 * math.pi * (freq * 4.2) * t)
                ) * decay * 0.40
                raw_left[start_s + i] += bell * 1.05
                raw_right[start_s + i] += bell * 0.95

        curr_time += note_dur

    # Normalize audio levels
    max_amp = max(
        0.001,
        max(abs(s) for s in raw_left),
        max(abs(s) for s in raw_right)
    )
    scale = 27000.0 / max_amp

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with wave.open(output_path, "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for i in range(total_samples):
            l_val = int(max(-32767, min(32767, raw_left[i] * scale)))
            r_val = int(max(-32767, min(32767, raw_right[i] * scale)))
            frames.extend(struct.pack("<hh", l_val, r_val))
        wav_file.writeframes(frames)

    return output_path


def synthesize_vocals(lyrics_lines: List[str], output_wav: str, duration_sec: float = 60.0) -> str:
    """
    Synthesizes cheerful, studio-quality neural singing/spoken preschool vocals.
    1. Tries Edge Neural TTS (en-US-AnaNeural / en-US-JennyNeural)
    2. Falls back to macOS speech with vocal master DSP
    """
    import asyncio
    os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)
    full_text = ". ".join(line.strip() for line in lyrics_lines if line.strip())

    # 1. Try Edge Neural TTS
    try:
        from audio.neural_tts import synthesize_edge_neural_tts
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except Exception:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, synthesize_edge_neural_tts(full_text, output_wav, voice="en-US-AnaNeural"))
                ok = future.result(timeout=15)
        else:
            ok = loop.run_until_complete(synthesize_edge_neural_tts(full_text, output_wav, voice="en-US-AnaNeural"))

        if ok and os.path.exists(output_wav) and os.path.getsize(output_wav) > 1000:
            return output_wav
    except Exception:
        pass

    # 2. Fallback to macOS speech
    say_bin = shutil.which("say")
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"

    if say_bin:
        temp_aiff = output_wav.replace(".wav", "_raw.aiff")
        cmd = [say_bin, "-v", "Samantha", "-r", "145", full_text, "-o", temp_aiff]
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode == 0 and os.path.exists(temp_aiff):
            filter_vocal = (
                "highpass=f=120, lowpass=f=9500, "
                "acompressor=threshold=-16dB:ratio=3:attack=15:release=120, "
                "aecho=0.8:0.7:30|50:0.25|0.18"
            )
            conv_cmd = [
                ffmpeg_bin, "-y",
                "-i", temp_aiff,
                "-af", filter_vocal,
                "-ar", "44100",
                "-ac", "2",
                output_wav
            ]
            subprocess.run(conv_cmd, capture_output=True)
            if os.path.exists(temp_aiff):
                os.remove(temp_aiff)
            if os.path.exists(output_wav):
                return output_wav

    return generate_nursery_melody(output_wav, duration_sec=duration_sec)


def generate_subtitles_srt(scenes: List[Dict[str, Any]], output_srt: str, total_duration_sec: float = 60.0) -> str:
    """
    Generates synchronized .srt subtitles covering the full requested video duration.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_srt)), exist_ok=True)

    def fmt_time(seconds: float) -> str:
        millis = int((seconds - int(seconds)) * 1000)
        s = int(seconds) % 60
        m = (int(seconds) // 60) % 60
        h = int(seconds) // 3600
        return f"{h:02d}:{m:02d}:{s:02d},{millis:03d}"

    srt_entries = []
    if not scenes:
        scenes = [{"duration": 15.0, "lyrics": "Singing our happy nursery song today!"}]

    # Check if exact start/end timestamps are provided
    has_timestamps = any(("start" in sc and "end" in sc) or ("start_time" in sc and "end_time" in sc) for sc in scenes)
    if has_timestamps:
        for idx, sc in enumerate(scenes, start=1):
            s_start = float(sc.get("start") if "start" in sc else sc.get("start_time", 0.0))
            s_end = float(sc.get("end") if "end" in sc else sc.get("end_time", s_start + float(sc.get("duration", 5.0))))
            lyrics = sc.get("line") or sc.get("lyrics") or sc.get("dialogue") or f"Musical Adventure Scene {idx}"
            if s_start >= total_duration_sec:
                break
            entry = f"{idx}\n{fmt_time(s_start)} --> {fmt_time(min(total_duration_sec, s_end))}\n{lyrics.strip()}\n"
            srt_entries.append(entry)
    else:
        current_sec = 0.5
        idx = 1
        while current_sec < total_duration_sec:
            sc = scenes[(idx - 1) % len(scenes)]
            dur = float(sc.get("duration", 6.0))
            end_sec = min(total_duration_sec, current_sec + dur - 0.5)
            lyrics = sc.get("lyrics") or sc.get("dialogue") or f"Musical Adventure Scene {idx}"

            entry = f"{idx}\n{fmt_time(current_sec)} --> {fmt_time(end_sec)}\n{lyrics}\n"
            srt_entries.append(entry)
            current_sec += dur
            idx += 1

    with open(output_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))

    return output_srt


def mix_soundtrack(music_wav: str, vocals_wav: str, output_final_audio: str) -> str:
    """
    Mixes rich nursery backing track with polished narration into a studio master audio file.
    """
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    os.makedirs(os.path.dirname(os.path.abspath(output_final_audio)), exist_ok=True)

    # Balance levels: Vocals clear at 1.0, Music balanced at 0.50
    cmd = [
        ffmpeg_bin, "-y",
        "-i", vocals_wav,
        "-i", music_wav,
        "-filter_complex",
        "[0:a]volume=1.0[v];[1:a]volume=0.50[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=2[out]",
        "-map", "[out]",
        "-ar", "44100",
        "-ac", "2",
        output_final_audio
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode == 0 and os.path.exists(output_final_audio):
        return output_final_audio

    if os.path.exists(music_wav):
        shutil.copyfile(music_wav, output_final_audio)
    return output_final_audio
