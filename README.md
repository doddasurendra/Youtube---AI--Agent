# Telugu YouTube AI Agent

An open-source automation pipeline to generate cinematic Telugu YouTube videos from a topic prompt. The agent produces story scripts with scenes, narration, visuals, subtitles, metadata, thumbnails, and optionally uploads to YouTube.

## Features

- FastAPI service + CLI runner
- Story-style Telugu scripts with scenes + dialogue
- Scene-wise timestamps
- AI image generation per scene
- Ken Burns motion on visuals (animated feel)
- Background music + optional SFX mixing
- Telugu subtitles burned into video
- Cinematic intro & outro
- Mobile-first 9:16 output for Shorts + Full videos
- Logging, retries, and graceful fallbacks

## Project Structure

```
 telugu-youtube-ai-agent/
 ├── .github/workflows/automation.yml
 ├── app/
 ├── docs/
 ├── examples/
 ├── tests/
 ├── .env.example
 ├── Dockerfile
 ├── requirements.txt
 └── README.md
```

## Setup

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment

Copy `.env.example` to `.env` and fill in the required values:

```bash
cp .env.example .env
```

Required keys:
- `OPENAI_API_KEY` for script, metadata, and image generation
- `TTS_LANGUAGE=te` and `TTS_VOICE=co.in` for Telugu narration
- Optional: `BGM_PATH` and `SFX_PATHS` (comma-separated) for audio layers
- YouTube credentials when using upload

## Usage

### CLI (Generate cinematic artifacts)

```bash
python -m app.main run "Topic: Indian Space Missions" \
  --video-type short \
  --short-duration 3 \
  --full-duration 20 \
  --style "Simple Telugu"
```

Artifacts are written under `outputs/<topic>/`.

### API

```bash
uvicorn app.main:app --reload --port 8000
```

Send a POST request to `/generate`:

```json
{
  "topic": "AI in Education",
  "video_type": "short",
  "short_duration": 3,
  "full_duration": 15,
  "category": "General",
  "style": "Simple Telugu"
}
```

## Validation

Run local validations for TTS/video/upload prerequisites:

```bash
python -m app.main validate --check-tts --check-video
```

- `--skip-network` defaults to `True` to avoid live gTTS calls.
- Set `--skip-network False` to fully validate Telugu TTS (requires network).
- For upload validation:

```bash
python -m app.main validate --check-upload \
  --client-secret client_secret.json \
  --token-path token.json
```

## YouTube Upload

1. Create OAuth credentials in Google Cloud Console.
2. Download `client_secret.json`.
3. Run the CLI with upload enabled:

```bash
python -m app.main run "AI in Education" --upload \
  --client-secret client_secret.json \
  --token-path token.json
```

If `YOUTUBE_TOKEN_KEY` is set, the token file is encrypted after login.

## GitHub Actions

- Runs tests on push and PRs
- Scheduled daily automation run
- Docker build job for deployments

Set GitHub Secrets for OpenAI, YouTube credentials, and container registry tokens.

## Deployment

### Docker

```bash
docker build -t telugu-youtube-ai-agent .
docker run --env-file .env -p 8000:8000 telugu-youtube-ai-agent
```

### Cloud (Railway/AWS)

1. Build and push the Docker image to a registry (GHCR/ECR).
2. Deploy the container to Railway or AWS ECS/Fargate.
3. Configure environment variables in the platform.
4. Schedule runs via GitHub Actions or platform cron.

## Maintenance Guide

- Rotate API keys periodically.
- Review generated scripts for accuracy.
- Monitor YouTube API quota.
- Update dependencies monthly.

## License

MIT License.
