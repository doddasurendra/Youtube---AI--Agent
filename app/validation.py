from __future__ import annotations

import logging
from pathlib import Path

from app.tts import synthesize_voice
from app.utils import ensure_ffmpeg

logger = logging.getLogger(__name__)


def validate_tts(output_dir: Path, language: str, voice: str, skip_network: bool) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "tts_validation.mp3"
    if skip_network:
        logger.info("Skipping live TTS validation (skip_network=True)")
        return output_path
    sample_text = "హలో! ఇది తెలుగు వాయిస్ పరీక్ష."  # Telugu sample
    synthesize_voice(sample_text, output_path, language=language, voice=voice)
    logger.info("TTS validation audio written to %s", output_path)
    return output_path


def validate_video(output_dir: Path) -> Path:
    ensure_ffmpeg()
    from moviepy.editor import AudioClip, ColorClip

    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / "video_validation.mp4"
    clip = ColorClip(size=(640, 360), color=(20, 24, 38)).set_duration(1)
    audio = AudioClip(lambda t: 0.0, duration=1, fps=44100)
    try:
        video = clip.set_audio(audio)
        video.write_videofile(
            str(video_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None,
        )
    finally:
        audio.close()
        clip.close()
    logger.info("Video validation output written to %s", video_path)
    return video_path


def validate_upload_requirements(client_secret: Path, token_path: Path) -> None:
    if not client_secret.exists():
        raise FileNotFoundError("client_secret.json missing for upload validation")
    if token_path.exists():
        logger.info("Token file found at %s", token_path)
    else:
        logger.info("Token file not found; upload will require OAuth login")
