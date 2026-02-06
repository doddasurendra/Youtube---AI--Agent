from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from app.image_gen import generate_scene_image
from app.intro_outro import build_intro_outro
from app.retry_utils import with_retry
from app.scenes import build_timestamps, parse_scenes
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

    scene_count = 6 if config.video_type.lower() == "short" else 12
    script = generate_script(
        topic=topic,
        style=config.style,
        language=config.language,
        video_type=config.video_type,
        short_duration=config.short_duration,
        full_duration=config.full_duration,
        scene_count=scene_count,
    )
    script_path = config.workdir / "script.txt"
    script_path.write_text(script, encoding="utf-8")
    logger.info("Script generated at %s", script_path)

    scenes = parse_scenes(script, default_duration_s=12)
    timeline = build_timestamps(scenes)

    audio_path = config.workdir / "narration.mp3"
    narration_text = "\n".join([scene.narration for scene in scenes])
    synthesize_voice(narration_text, audio_path, language=config.language, voice=config.voice)
    logger.info("Audio generated at %s", audio_path)

    thumbnail_path = config.workdir / "thumbnail.png"
    create_thumbnail(topic, thumbnail_path)
    logger.info("Thumbnail generated at %s", thumbnail_path)

    size = (1080, 1920)
    intro_path, outro_path = build_intro_outro(topic, size)

    image_timeline: list[tuple[Path, str, float, float]] = []
    for scene, start, end in timeline:
        image_path = config.workdir / f"scene_{scene.index}.png"
        generate_scene_image(scene.visual_prompt, image_path)
        subtitle = f"{scene.narration} {scene.dialogue}".strip()
        image_timeline.append((image_path, subtitle, start + 3, end + 3))

    intro_duration = 3
    outro_duration = 3
    image_timeline.insert(0, (intro_path, "", 0, intro_duration))
    final_end = (timeline[-1][2] if timeline else 0) + intro_duration
    image_timeline.append((outro_path, "", final_end, final_end + outro_duration))

    video_path = config.workdir / "video.mp4"
    bgm_path = Path(os.getenv("BGM_PATH", "")) if os.getenv("BGM_PATH") else None
    sfx_paths = [Path(p) for p in os.getenv("SFX_PATHS", "").split(",") if p]
    create_video(image_timeline, audio_path, bgm_path, sfx_paths, video_path, size=size)
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
