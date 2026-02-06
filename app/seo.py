from __future__ import annotations

import json
import logging
import os

from app.retry_utils import with_retry

logger = logging.getLogger(__name__)


def _fallback_metadata(topic: str) -> dict[str, str]:
    return {
        "title": f"{topic} | తెలుగు వివరణ",
        "description": f"ఈ వీడియోలో {topic} గురించి సులభమైన తెలుగు వివరణ ఉంటుంది.",
        "tags": "telugu,education,technology,health,finance,motivation",
    }


@with_retry(attempts=3, wait_seconds=2, backoff=2)
def generate_metadata(topic: str, script: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY missing, using fallback metadata")
        return json.dumps(_fallback_metadata(topic), ensure_ascii=False, indent=2)

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    prompt = (
        "Generate SEO metadata for a Telugu YouTube video. "
        "Return JSON with title, description, tags. "
        f"Topic: {topic}. Script: {script[:500]}"
    )
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )
    return response.choices[0].message.content.strip()
