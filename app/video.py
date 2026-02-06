from __future__ import annotations

import logging
from pathlib import Path

from app.retry_utils import with_retry
from app.utils import ensure_ffmpeg

logger = logging.getLogger(__name__)


@with_retry(attempts=3, wait_seconds=2, backoff=2)
def create_video(audio_path: Path, image_path: Path, output_path: Path) -> None:
    logger.info("Building video")
    ensure_ffmpeg()
    from moviepy.editor import AudioFileClip, ImageClip

    audio = None
    image = None
    try:
        audio = AudioFileClip(str(audio_path))
        image = ImageClip(str(image_path)).set_duration(audio.duration)
        video = image.set_audio(audio)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        video.write_videofile(
            str(output_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None,
        )
    finally:
        if image:
            image.close()
        if audio:
            audio.close()
