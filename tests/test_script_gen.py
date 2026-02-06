from app.script_gen import generate_script


def test_generate_script_fallback(monkeypatch: object) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    script = generate_script(
        topic="Test",
        style="Simple Telugu",
        language="te",
        video_type="Auto",
        short_duration=3,
        full_duration=15,
        scene_count=3,
    )
    assert "OPENAI_API_KEY" in script
