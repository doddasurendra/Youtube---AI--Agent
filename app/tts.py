from __future__ import annotations

import logging
from pathlib import Path

from app.retry_utils import with_retry

logger = logging.getLogger(__name__)


@with_retry(attempts=3, wait_seconds=2, backoff=2)
def synthesize_voice(text: str, output_path: Path, language: str, voice: str) -> None:
    logger.info("Generating TTS audio")
    try:
        from gtts import gTTS
        from gtts.tts import gTTSError

        tts = gTTS(text=text, lang=language, tld=voice)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tts.save(str(output_path))
    except gTTSError as exc:
        logger.error("TTS generation failed: %s", exc)
        raise RuntimeError("Failed to generate TTS audio") from exc
