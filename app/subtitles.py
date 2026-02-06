from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def render_subtitle(text: str, size: tuple[int, int]) -> Path:
    width, height = size
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    margin = 20
    max_width = width - 2 * margin
    lines = _wrap_text(text, font, max_width, draw)
    y = height - margin - (len(lines) * 14)
    for line in lines:
        text_width = draw.textlength(line, font=font)
        x = (width - text_width) / 2
        draw.rectangle(
            (x - 10, y - 2, x + text_width + 10, y + 14),
            fill=(0, 0, 0, 180),
        )
        draw.text((x, y), line, fill=(255, 255, 255, 255), font=font)
        y += 16
    output_path = Path("subtitles") / f"subtitle_{abs(hash(text))}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        current.append(word)
        width = draw.textlength(" ".join(current), font=font)
        if width > max_width:
            current.pop()
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines
