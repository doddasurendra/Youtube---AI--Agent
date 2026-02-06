from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from app.retry_utils import with_retry
from app.utils import decrypt_file, encrypt_file

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _load_credentials(client_secret_path: Path, token_path: Path):
    if not client_secret_path.exists():
        raise FileNotFoundError("client_secret.json not found")

    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    encryption_key = os.getenv("YOUTUBE_TOKEN_KEY")
    if token_path.exists() and encryption_key:
        decrypted = decrypt_file(token_path, encryption_key)
        token_data = json.loads(decrypted.decode("utf-8"))
        return Credentials.from_authorized_user_info(token_data, SCOPES)

    if token_path.exists() and not encryption_key:
        token_data = json.loads(token_path.read_text(encoding="utf-8"))
        return Credentials.from_authorized_user_info(token_data, SCOPES)

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    if encryption_key:
        encrypt_file(token_path, encryption_key)
        logger.info("Encrypted YouTube token file")
    return creds


@with_retry(attempts=3, wait_seconds=2, backoff=2)
def upload_video(
    video_path: Path,
    metadata_path: Path,
    thumbnail_path: Path,
    client_secret_path: Path,
    token_path: Path,
) -> None:
    if not video_path.exists():
        raise FileNotFoundError("video.mp4 not found")
    if not metadata_path.exists():
        raise FileNotFoundError("metadata.json not found")

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = _load_credentials(client_secret_path, token_path)
    service = build("youtube", "v3", credentials=creds)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    request = service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": metadata.get("title"),
                "description": metadata.get("description"),
                "tags": metadata.get("tags", "").split(","),
                "categoryId": os.getenv("YOUTUBE_CATEGORY", "27"),
            },
            "status": {"privacyStatus": os.getenv("YOUTUBE_PRIVACY", "private")},
        },
        media_body=MediaFileUpload(str(video_path), resumable=True),
    )

    response = request.execute()
    video_id = response.get("id")
    logger.info("Uploaded video with id %s", video_id)

    if thumbnail_path.exists():
        service.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumbnail_path)),
        ).execute()
        logger.info("Thumbnail uploaded")
