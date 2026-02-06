from __future__ import annotations

import logging
from pathlib import Path

from moviepy.editor import CompositeVideoClip, ImageClip

from app.audio import mix_background
from app.subtitles import render_subtitle
from app.utils import ensure_ffmpeg

logger = logging.getLogger(__name__)


def _ken_burns(image_path: Path, duration: float, size: tuple[int, int]) -> ImageClip:
    clip = ImageClip(str(image_path)).resize(height=size[1])
    clip = clip.set_duration(duration)
    zoom = 1.1
    return clip.fx(
        lambda c: c.resize(lambda t: 1 + (zoom - 1) * (t / duration))
    ).set_position("center")


def create_video(
    timeline: list[tuple[Path, str, float, float]],
    narration_path: Path,
    bgm_path: Path | None,
    sfx_paths: list[Path],
    output_path: Path,
    size: tuple[int, int] = (1080, 1920),
) -> None:
    logger.info("Building cinematic video")
    ensure_ffmpeg()

    clips: list[ImageClip] = []
    subtitle_clips: list[ImageClip] = []
    for image_path, subtitle, start, end in timeline:
        scene_clip = _ken_burns(image_path, end - start, size)
        scene_clip = scene_clip.set_start(start)
        clips.append(scene_clip)

        subtitle_image = render_subtitle(subtitle, size)
        subtitle_clip = ImageClip(str(subtitle_image)).set_start(start).set_duration(end - start)
        subtitle_clips.append(subtitle_clip)

    composite = CompositeVideoClip(clips + subtitle_clips, size=size)
    composite = composite.set_audio(mix_background(narration_path, bgm_path, sfx_paths))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    composite.write_videofile(
        str(output_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )
