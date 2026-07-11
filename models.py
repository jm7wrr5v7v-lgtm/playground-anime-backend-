from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnimeStyleVariant(str, Enum):
    shonen = "shonen"
    shojo = "shojo"
    ghibli_inspired = "ghibliInspired"
    chibi = "chibi"


class AspectRatio(str, Enum):
    square = "1:1"
    portrait = "3:4"
    landscape = "4:3"


class GenerationRequest(BaseModel):
    prompt: str = ""
    source_image_data: Optional[str] = Field(default=None, alias="sourceImageData")
    style: AnimeStyleVariant = AnimeStyleVariant.shonen
    aspect_ratio: AspectRatio = Field(default=AspectRatio.square, alias="aspectRatio")

    model_config = {"populate_by_name": True}


class GeneratedImage(BaseModel):
    id: UUID
    image_url: str = Field(alias="imageURL")
    created_at: datetime = Field(alias="createdAt")
    style: AnimeStyleVariant

    model_config = {"populate_by_name": True}
