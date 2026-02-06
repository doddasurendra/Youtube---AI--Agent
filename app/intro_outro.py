from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def build_intro_outro(title: str, size: tuple[int, int]) -> tuple[Path, Path]:
    intro_path = Path("assets") / "intro.png"
    outro_path = Path("assets") / "outro.png"
    intro_path.parent.mkdir(parents=True, exist_ok=True)

    for path, text in [(intro_path, f"{title}\nTelugu AI Studio"), (outro_path, "ధన్యవాదాలు")]:
        image = Image.new("RGB", size, color=(5, 8, 20))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.text((60, size[1] // 2), text, fill=(255, 215, 0), font=font)
        image.save(path)

    return intro_path, outro_path
