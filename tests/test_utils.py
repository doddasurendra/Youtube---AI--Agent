from importlib.util import find_spec
from pathlib import Path

import pytest

from app.utils import decrypt_file, encrypt_file


def test_encrypt_decrypt_roundtrip(tmp_path: Path) -> None:
    if not find_spec("cryptography"):
        pytest.skip("cryptography not installed")
    key = "Y8ydN4dh4I_xSkc8Zy5QvEqnDF8A5t4cjGQfjhG2iGE="
    sample = tmp_path / "token.json"
    sample.write_text("secret", encoding="utf-8")

    encrypt_file(sample, key)
    decrypted = decrypt_file(sample, key)

    assert decrypted.decode("utf-8") == "secret"
