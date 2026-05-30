"""
ChristianMind AI - Image Route
=============================
API endpoint for image generation with safety classification and prompt sanitization.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from backend.core.image_pipeline import generate_christian_image


router = APIRouter()


class ImageRequest(BaseModel):
    """Request model for image endpoint."""
    prompt: str = Field(..., description="The image prompt")
    session_id: str = Field(default="", description="Session identifier")


class ImageResponse(BaseModel):
    """Response model for image endpoint."""
    success: bool
    image_url: Optional[str] = None
    sanitized_prompt: Optional[str] = None
    original_prompt: Optional[str] = None
    note: Optional[str] = None
    error: Optional[str] = None


@router.post("", response_model=ImageResponse)
async def generate_image(request: ImageRequest) -> ImageResponse:
    """
    Generate a Christian-themed image.

    Pipeline:
    1. Safety classification - block inappropriate requests
    2. Prompt sanitization - rewrite for theological appropriateness
    3. Image generation - via Pollinations.ai (no API key)
    4. URL verification - ensure the image is accessible

    Returns:
        ImageResponse with success status and image URL if successful
    """
    result = generate_christian_image(request.prompt)

    if result["success"]:
        return ImageResponse(
            success=True,
            image_url=result["image_url"],
            sanitized_prompt=result.get("sanitized_prompt"),
            original_prompt=result.get("original_prompt"),
            note=result.get("note"),
            error=None
        )
    else:
        return ImageResponse(
            success=False,
            image_url=None,
            sanitized_prompt=result.get("sanitized_prompt"),
            original_prompt=request.prompt,
            note=None,
            error=result.get("error", "Unknown error")
        )
