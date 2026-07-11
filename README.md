# Playground Anime — Backend

A FastAPI service that receives generation requests from the iOS app,
calls fal.ai for the actual anime-style image generation, and enforces
free-tier quotas.

## Files

- `main.py` — API routes (`/v1/generate`, `/v1/usage`, `/health`)
- `models.py` — request/response shapes, matching the Swift app's JSON exactly
- `fal_service.py` — the fal.ai integration (text-to-image + selfie image-to-image)
- `quota.py` — in-memory usage tracking (placeholder — swap for a real DB)

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export FAL_KEY="your-fal-api-key"
export FREE_TIER_MONTHLY_LIMIT=5

uvicorn main:app --reload --port 8000
