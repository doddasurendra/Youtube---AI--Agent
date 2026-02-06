from __future__ import annotations

import logging
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def generate_scene_image(prompt: str, output_path: Path) -> Path:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.images.generate(
            model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
            prompt=prompt,
            size="1024x1024",
        )
        image_url = response.data[0].url
        if image_url:
            import requests

            content = requests.get(image_url, timeout=30).content
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(content)
            return output_path

    logger.warning("OPENAI_API_KEY missing or image generation failed, using placeholder")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1024, 1024), color=(12, 16, 28))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((40, 40), prompt[:120], fill=(255, 215, 0), font=font)
    image.save(output_path)
    return output_path
