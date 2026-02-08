from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


JPEG_QUALITY = 88


def get_cropped_image_variant(image_field_file, variant_name: str, size: tuple[int, int]) -> str:
    """
    Return URL to a cropped image variant.

    The variant is created once and stored under `.../_variants/`.
    If source file changes (for local filesystem storage), variant is regenerated.
    """
    if not image_field_file:
        return ""

    source_name = image_field_file.name
    if not source_name:
        return ""

    storage = image_field_file.storage
    width, height = size
    variant_file_name = _variant_file_name(source_name, variant_name, width, height)

    needs_regeneration = not storage.exists(variant_file_name)
    if not needs_regeneration and _storage_supports_paths(storage):
        needs_regeneration = _is_older_than_source(storage, source_name, variant_file_name)

    if needs_regeneration:
        try:
            variant_content = _build_variant_content(storage, source_name, (width, height))
            if storage.exists(variant_file_name):
                storage.delete(variant_file_name)
            storage.save(variant_file_name, ContentFile(variant_content))
        except Exception:
            return image_field_file.url

    return storage.url(variant_file_name)


def _variant_file_name(source_name: str, variant_name: str, width: int, height: int) -> str:
    source_path = Path(source_name)
    return str(
        source_path.parent / "_variants" / f"{source_path.stem}__{variant_name}_{width}x{height}.jpg"
    )


def _build_variant_content(storage, source_name: str, size: tuple[int, int]) -> bytes:
    with storage.open(source_name, "rb") as source_file:
        with Image.open(source_file) as image:
            image = ImageOps.exif_transpose(image)
            cropped = ImageOps.fit(
                image,
                size,
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            cropped = _convert_to_rgb(cropped)
            buffer = BytesIO()
            cropped.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            return buffer.getvalue()


def _convert_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode == "RGB":
        return image

    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, "white")
        alpha = image.getchannel("A")
        background.paste(image, mask=alpha)
        return background

    if image.mode == "P":
        return image.convert("RGBA").convert("RGB")

    return image.convert("RGB")


def _storage_supports_paths(storage) -> bool:
    return callable(getattr(storage, "path", None))


def _is_older_than_source(storage, source_name: str, variant_name: str) -> bool:
    try:
        source_path = storage.path(source_name)
        variant_path = storage.path(variant_name)
    except (NotImplementedError, OSError, ValueError):
        return False

    try:
        return os.path.getmtime(variant_path) < os.path.getmtime(source_path)
    except OSError:
        return True
