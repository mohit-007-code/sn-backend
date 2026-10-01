import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status


UPLOAD_DIR = Path("uploads")

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024

async def save_image(file: UploadFile, folder: str = "profiles") -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are allowed",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size must not exceed 5 MB",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty",
        )
    target_dir = UPLOAD_DIR / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    filename = f"{uuid.uuid4()}{extension}"

    file_path = target_dir / filename

    file_path.write_bytes(content)

    return f"/uploads/{folder}/{filename}"