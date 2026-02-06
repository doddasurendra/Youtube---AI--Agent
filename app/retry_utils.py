from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import AgentConfig, run_pipeline
from app.logging_config import configure_logging
from app.upload import upload_video
from app.validation import validate_tts, validate_upload_requirements, validate_video

load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Telugu YouTube AI Agent")
cli = typer.Typer(add_completion=False)


class TopicRequest(BaseModel):
    topic: str
    video_type: str = "Auto"
    short_duration: int = 3
    full_duration: int = 15
    category: str = "General"
    style: str = "Simple Telugu"


@app.post("/generate")
async def generate(req: TopicRequest) -> dict[str, str]:
    config = AgentConfig(
        workdir=Path(os.getenv("OUTPUT_DIR", "outputs")) / req.topic.replace(" ", "_"),
        voice=os.getenv("TTS_VOICE", "co.in"),
        language=os.getenv("TTS_LANGUAGE", "te"),
        style=req.style,
        short_duration=req.short_duration,
        full_duration=req.full_duration,
        video_type=req.video_type,
    )
    artifacts = run_pipeline(req.topic, config)
    return {key: str(path) for key, path in artifacts.items()}


@cli.command()
def run(
    topic: str = typer.Argument(..., help="Topic in Telugu or English"),
    video_type: str = typer.Option("Auto", help="Auto/short/full"),
    short_duration: int = typer.Option(3, help="Short duration in minutes"),
    full_duration: int = typer.Option(15, help="Full duration in minutes"),
    style: str = typer.Option("Simple Telugu", help="Content style"),
    upload: bool = typer.Option(False, help="Upload to YouTube"),
    client_secret: Optional[Path] = typer.Option(
        None, help="Path to client_secret.json"
    ),
    token_path: Optional[Path] = typer.Option(None, help="Path to token.json"),
) -> None:
    config = AgentConfig(
        workdir=Path(os.getenv("OUTPUT_DIR", "outputs")) / topic.replace(" ", "_"),
        voice=os.getenv("TTS_VOICE", "co.in"),
        language=os.getenv("TTS_LANGUAGE", "te"),
        style=style,
        short_duration=short_duration,
        full_duration=full_duration,
        video_type=video_type,
    )
    artifacts = run_pipeline(topic, config)
    logger.info("Artifacts: %s", artifacts)

    if upload:
        if not client_secret or not token_path:
            raise typer.BadParameter("client_secret and token_path are required")
        upload_video(
            video_path=artifacts["video"],
            metadata_path=artifacts["metadata"],
            thumbnail_path=artifacts["thumbnail"],
            client_secret_path=client_secret,
            token_path=token_path,
        )


@cli.command()
def validate(
    output_dir: Path = typer.Option(
        Path("validation_outputs"), help="Directory for validation artifacts"
    ),
    check_tts: bool = typer.Option(True, help="Validate TTS generation"),
    check_video: bool = typer.Option(True, help="Validate video generation"),
    check_upload: bool = typer.Option(False, help="Validate upload prerequisites"),
    skip_network: bool = typer.Option(
        True, help="Skip live TTS validation that requires network"
    ),
    client_secret: Optional[Path] = typer.Option(
        None, help="Path to client_secret.json"
    ),
    token_path: Optional[Path] = typer.Option(None, help="Path to token.json"),
) -> None:
    logger.info("Running validation checks")
    if check_tts:
        validate_tts(
            output_dir,
            language=os.getenv("TTS_LANGUAGE", "te"),
            voice=os.getenv("TTS_VOICE", "co.in"),
            skip_network=skip_network,
        )
    if check_video:
        validate_video(output_dir)
    if check_upload:
        if not client_secret or not token_path:
            raise typer.BadParameter("client_secret and token_path are required")
        validate_upload_requirements(client_secret, token_path)
    logger.info("Validation complete")


if __name__ == "__main__":
    cli()
