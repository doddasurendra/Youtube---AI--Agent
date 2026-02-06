from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def create_thumbnail(title: str, output_path: Path) -> None:
    logger.info("Creating thumbnail")
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), color=(20, 24, 38))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text = title[:80]
    text_width = draw.textlength(text, font=font)
    draw.text(
        ((width - text_width) / 2, height / 2 - 10),
        text,
        fill=(255, 215, 0),
        font=font,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
