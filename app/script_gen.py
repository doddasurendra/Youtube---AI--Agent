from __future__ import annotations

import logging
import os

from app.retry_utils import with_retry

logger = logging.getLogger(__name__)


def _build_prompt(
    topic: str,
    style: str,
    language: str,
    video_type: str,
    short_duration: int,
    full_duration: int,
    scene_count: int,
) -> str:
    return (
        "You are a Telugu storyteller. Write a cinematic script with scenes and dialogues. "
        "Each scene should include: Scene title, Narration, Dialogue, Visual, SFX, Duration. "
        "Write in natural, friendly Telugu suitable for all ages. "
        "No misleading information. "
        f"Topic: {topic}. "
        f"Style: {style}. "
        f"Language: {language}. "
        f"Video type: {video_type}. "
        f"Short duration: {short_duration} minutes. "
        f"Full duration: {full_duration} minutes. "
        f"Scenes: {scene_count}. "
        "Return structured script with Scene 1..N."
    )


@with_retry(attempts=3, wait_seconds=2, backoff=2)
def generate_script(
    topic: str,
    style: str,
    language: str,
    video_type: str,
    short_duration: int,
    full_duration: int,
    scene_count: int,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY missing, returning placeholder script")
        return (
            f"Scene 1: {topic}\n"
            "Narration: ఇది డెమో కథ. OPENAI_API_KEY సెట్ చేయండి.\n"
            "Dialogue: పాత్ర 1: హలో!\n"
            "Visual: Telugu cinematic illustration.\n"
            "SFX: soft wind\n"
            "Duration: 12"
        )

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(
        topic=topic,
        style=style,
        language=language,
        video_type=video_type,
        short_duration=short_duration,
        full_duration=full_duration,
        scene_count=scene_count,
    )
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
