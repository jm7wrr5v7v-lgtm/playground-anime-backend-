import base64
import os
import tempfile

import fal_client

from models import AnimeStyleVariant, AspectRatio

TEXT_TO_IMAGE_MODEL = os.environ.get("FAL_TEXT_MODEL", "fal-ai/fast-sdxl")
IMAGE_TO_IMAGE_MODEL = os.environ.get("FAL_IMG2IMG_MODEL", "fal-ai/fast-sdxl/image-to-image")

STYLE_PROMPT_PREFIXES = {
    AnimeStyleVariant.shonen: "anime screenshot, shonen manga style, bold linework, dynamic pose,",
    AnimeStyleVariant.shojo: "anime style, shojo manga aesthetic, soft shading, pastel palette, large expressive eyes,",
    AnimeStyleVariant.ghibli_inspired: "hand-painted anime style, soft painterly background, warm natural lighting,",
    AnimeStyleVariant.chibi: "chibi anime style, cute stylized proportions, simple background,",
}

ASPECT_RATIO_TO_SIZE = {
    AspectRatio.square: "square_hd",
    AspectRatio.portrait: "portrait_4_3",
    AspectRatio.landscape: "landscape_4_3",
}


async def generate_image(
    prompt: str,
    style: AnimeStyleVariant,
    source_image_data: str | None,
    aspect_ratio: AspectRatio,
) -> str:
    styled_prompt = f"{STYLE_PROMPT_PREFIXES[style]} {prompt}".strip()
    image_size = ASPECT_RATIO_TO_SIZE[aspect_ratio]

    if source_image_data:
        image_url = await _upload_source_image(source_image_data)
        result = await fal_client.run_async(
            IMAGE_TO_IMAGE_MODEL,
            arguments={
                "prompt": styled_prompt,
                "image_url": image_url,
                "strength": 0.65,
                "image_size": image_size,
            },
        )
    else:
        result = await fal_client.run_async(
            TEXT_TO_IMAGE_MODEL,
            arguments={
                "prompt": styled_prompt,
                "image_size": image_size,
                "num_inference_steps": 28,
            },
        )

    images = result.get("images") or []
    if not images:
        raise RuntimeError("Model returned no images")

    return images[0]["url"]


async def _upload_source_image(base64_data: str) -> str:
    raw_bytes = base64.b64decode(base64_data)

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        tmp_file.write(raw_bytes)
        tmp_path = tmp_file.name

    uploaded_url = await fal_client.upload_file_async(tmp_path)
    os.unlink(tmp_path)
    return uploaded_url
