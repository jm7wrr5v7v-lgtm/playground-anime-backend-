import os
import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import GenerationRequest, GeneratedImage
from fal_service import generate_image
from quota import QuotaStore

app = FastAPI(title="Playground Anime Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

quota_store = QuotaStore()

FREE_TIER_MONTHLY_LIMIT = int(os.environ.get("FREE_TIER_MONTHLY_LIMIT", "5"))


def _user_id_from_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return authorization.removeprefix("Bearer ").strip()


@app.post("/v1/generate", response_model=GeneratedImage)
async def generate(request: GenerationRequest, authorization: str | None = Header(default=None)):
    user_id = _user_id_from_token(authorization)

    is_subscribed = quota_store.is_subscribed(user_id)
    if not is_subscribed:
        used = quota_store.get_usage_this_month(user_id)
        if used >= FREE_TIER_MONTHLY_LIMIT:
            raise HTTPException(status_code=429, detail="Free tier quota exceeded")

    if not request.prompt and not request.source_image_data:
        raise HTTPException(status_code=400, detail="Provide a prompt or a source image")

    try:
        image_url = await generate_image(
            prompt=request.prompt,
            style=request.style,
            source_image_data=request.source_image_data,
            aspect_ratio=request.aspect_ratio,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Generation failed: {exc}") from exc

    if not is_subscribed:
        quota_store.record_usage(user_id)

    return GeneratedImage(
        id=uuid.uuid4(),
        image_url=image_url,
        created_at=datetime.now(timezone.utc),
        style=request.style,
    )


@app.get("/v1/usage")
async def usage(authorization: str | None = Header(default=None)):
    user_id = _user_id_from_token(authorization)
    return {
        "used_this_month": quota_store.get_usage_this_month(user_id),
        "limit": FREE_TIER_MONTHLY_LIMIT,
        "is_subscribed": quota_store.is_subscribed(user_id),
    }


@app.get("/health")
async def health():
    return {"status": "ok", "time": time.time()}
