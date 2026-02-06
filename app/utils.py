from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def encrypt_file(path: Path, key: str) -> None:
    from cryptography.fernet import Fernet

    data = path.read_bytes()
    fernet = Fernet(key)
    path.write_bytes(fernet.encrypt(data))


def decrypt_file(path: Path, key: str) -> bytes:
    from cryptography.fernet import Fernet

    data = path.read_bytes()
    fernet = Fernet(key)
    return fernet.decrypt(data)


def ensure_ffmpeg() -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg not found. Please install ffmpeg and retry.")
