from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Scene:
    index: int
    title: str
    narration: str
    dialogue: str
    duration_s: float
    visual_prompt: str
    sfx: str


def _parse_line_value(line: str) -> str:
    return line.split(":", 1)[1].strip()


def parse_scenes(script: str, default_duration_s: float) -> list[Scene]:
    scenes: list[Scene] = []
    current: dict[str, str] = {}
    for raw_line in script.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.lower().startswith("scene"):
            if current:
                scenes.append(_build_scene(current, default_duration_s))
                current = {}
            current["title"] = line
        elif ":" in line:
            key = line.split(":", 1)[0].strip().lower()
            current[key] = _parse_line_value(line)
    if current:
        scenes.append(_build_scene(current, default_duration_s))
    return scenes


def _build_scene(data: dict[str, str], default_duration_s: float) -> Scene:
    index = len(data.get("title", "scene").split())
    return Scene(
        index=index,
        title=data.get("title", "Scene"),
        narration=data.get("narration", data.get("story", "")),
        dialogue=data.get("dialogue", ""),
        duration_s=float(data.get("duration", default_duration_s)),
        visual_prompt=data.get("visual", "Cinematic Telugu scene"),
        sfx=data.get("sfx", ""),
    )


def build_timestamps(scenes: Iterable[Scene]) -> list[tuple[Scene, float, float]]:
    timeline: list[tuple[Scene, float, float]] = []
    current = 0.0
    for scene in scenes:
        start = current
        end = start + scene.duration_s
        timeline.append((scene, start, end))
        current = end
    return timeline
