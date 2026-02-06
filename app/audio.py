from __future__ import annotations

import logging
from pathlib import Path

from moviepy.editor import AudioFileClip, CompositeAudioClip

logger = logging.getLogger(__name__)


def mix_background(
    narration_path: Path,
    bgm_path: Path | None,
    sfx_paths: list[Path],
) -> AudioFileClip:
    narration = AudioFileClip(str(narration_path))
    clips = [narration]

    if bgm_path and bgm_path.exists():
        bgm = AudioFileClip(str(bgm_path)).volumex(0.2).set_duration(narration.duration)
        clips.append(bgm)
    else:
        logger.info("No background music provided")

    for sfx_path in sfx_paths:
        if sfx_path.exists():
            clips.append(AudioFileClip(str(sfx_path)).volumex(0.5))

    return CompositeAudioClip(clips)
