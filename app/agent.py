from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from app.retry_utils import with_retry
from app.script_gen import generate_script
from app.seo import generate_metadata
from app.thumbnail import create_thumbnail
from app.tts import synthesize_voice
from app.video import create_video

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    workdir: Path
    voice: str
    language: str
    style: str
    short_duration: int
    full_duration: int
    video_type: str


@with_retry(attempts=3, wait_seconds=2, backoff=2)
def run_pipeline(topic: str, config: AgentConfig) -> dict[str, Path]:
    logger.info("Starting pipeline for topic: %s", topic)
    config.workdir.mkdir(parents=True, exist_ok=True)

    script = generate_script(
        topic=topic,
        style=config.style,
        language=config.language,
        video_type=config.video_type,
        short_duration=config.short_duration,
        full_duration=config.full_duration,
    )
    script_path = config.workdir / "script.txt"
    script_path.write_text(script, encoding="utf-8")
    logger.info("Script generated at %s", script_path)

    audio_path = config.workdir / "narration.mp3"
    synthesize_voice(script, audio_path, language=config.language, voice=config.voice)
    logger.info("Audio generated at %s", audio_path)

    thumbnail_path = config.workdir / "thumbnail.png"
    create_thumbnail(topic, thumbnail_path)
    logger.info("Thumbnail generated at %s", thumbnail_path)

    video_path = config.workdir / "video.mp4"
    create_video(audio_path, thumbnail_path, video_path)
    logger.info("Video generated at %s", video_path)

    metadata = generate_metadata(topic, script)
    metadata_path = config.workdir / "metadata.json"
    metadata_path.write_text(metadata, encoding="utf-8")
    logger.info("Metadata generated at %s", metadata_path)

    logger.info("Pipeline completed")
    return {
        "script": script_path,
        "audio": audio_path,
        "thumbnail": thumbnail_path,
        "video": video_path,
        "metadata": metadata_path,
    }
