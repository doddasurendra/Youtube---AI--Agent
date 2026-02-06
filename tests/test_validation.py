from pathlib import Path

from app.validation import validate_tts


def test_validate_tts_skip_network(tmp_path: Path) -> None:
    output = validate_tts(tmp_path, language="te", voice="co.in", skip_network=True)
    assert output == tmp_path / "tts_validation.mp3"
