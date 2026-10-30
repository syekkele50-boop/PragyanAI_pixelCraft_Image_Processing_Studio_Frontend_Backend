import math
import random

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def resize_max_side(image, size):
    """Resize while preserving aspect ratio."""
    size = max(1, int(size))
    image = image.convert("RGB")
    width, height = image.size

    scale = size / max(width, height)
    new_size = (
        max(1, round(width * scale)),
        max(1, round(height * scale))
    )
    return image.resize(new_size, Image.Resampling.LANCZOS)


def grayscale(image):
    return ImageOps.grayscale(image).convert("RGB")


def pencil_sketch(image):
    gray = ImageOps.grayscale(image)
    inverted = ImageOps.invert(gray)
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=10))

    gray_array = np.asarray(gray, dtype=np.float32)
    blur_array = np.asarray(blurred, dtype=np.float32)

    result = gray_array * 255 / np.maximum(1, 255 - blur_array)
    result = np.clip(result, 0, 255).astype(np.uint8)

    return Image.fromarray(result).convert("RGB")


def blend_images(image, image2, alpha=0.5):
    if image2 is None:
        raise ValueError("This operation requires a second image.")

    image = image.convert("RGBA")
    image2 = image2.convert("RGBA").resize(image.size)

    alpha = max(0.0, min(1.0, float(alpha)))
    return Image.blend(image, image2, alpha).convert("RGB")


def replace_background(image, background=None,
                       color="#ffffff", threshold=45):
    """
    Simple background replacement.
    Works best with a plain, evenly colored background.
    It is not an AI background-removal model.
    """
    image = image.convert("RGB")
    pixels = np.asarray(image).astype(np.float32)
    height, width, _ = pixels.shape

    corners = np.array([
        pixels[0, 0],
        pixels[0, width - 1],
        pixels[height - 1, 0],
        pixels[height - 1, width - 1]
    ])
    bg_color = np.median(corners, axis=0)

    distance = np.sqrt(np.sum((pixels - bg_color) ** 2, axis=2))
    mask = distance > float(threshold)

    # Smooth the edge slightly.
    alpha = Image.fromarray(
        (mask.astype(np.uint8) * 255), mode="L"
    ).filter(ImageFilter.GaussianBlur(radius=1.2))

    if background is not None:
        new_background = background.convert("RGB").resize(image.size)
    else:
        new_background = Image.new("RGB", image.size, color)

    new_background.paste(image, (0, 0), alpha)
    return new_background


def pixelate(image, size=32):
    """Reduce the longest side to the requested pixel dimension."""
    return resize_max_side(image, size)


def sharpen_and_resize(image, size=64):
    sharpened = ImageEnhance.Sharpness(image.convert("RGB")).enhance(2.0)
    return resize_max_side(sharpened, size)


def add_or_subtract(image, image2, operation="add"):
    if image2 is None:
        raise ValueError("This operation requires a second image.")

    image = image.convert("RGB")
    image2 = image2.convert("RGB").resize(image.size)

    a = np.asarray(image).astype(np.int16)
    b = np.asarray(image2).astype(np.int16)

    if operation == "subtract":
        result = a - b
    else:
        result = a + b

    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


def add_noise(image, strength=20, noise_type="gaussian"):
    array = np.asarray(image.convert("RGB")).astype(np.float32)
    strength = max(0, min(100, float(strength)))

    if noise_type == "salt_pepper":
        result = array.copy()
        rng = np.random.default_rng()

        random_map = rng.random(array.shape[:2])
        result[random_map < strength / 200] = 0
        result[random_map > 1 - strength / 200] = 255
    else:
        rng = np.random.default_rng()
        noise = rng.normal(0, strength, array.shape)
        result = array + noise

    return Image.fromarray(
        np.clip(result, 0, 255).astype(np.uint8)
    )


def make_collage(images):
    if not images:
        raise ValueError("Upload at least one image for a collage.")

    tile_width = 320
    tile_height = 240
    columns = 2
    rows = math.ceil(len(images) / columns)

    canvas = Image.new(
        "RGB",
        (columns * tile_width, rows * tile_height),
        "white"
    )

    for index, image in enumerate(images):
        tile = ImageOps.fit(
            image.convert("RGB"),
            (tile_width, tile_height)
        )
        x = (index % columns) * tile_width
        y = (index // columns) * tile_height
        canvas.paste(tile, (x, y))

    return canvas


def apply_operation(image, operation, image2=None, options=None):
    options = options or {}

    if operation == "grayscale":
        return grayscale(image)

    if operation == "sketch":
        return pencil_sketch(image)

    if operation == "blend":
        return blend_images(
            image, image2,
            options.get("alpha", 0.5)
        )

    if operation == "background":
        return replace_background(
            image,
            background=image2,
            color=options.get("background_color", "#ffffff"),
            threshold=options.get("threshold", 45)
        )

    if operation == "pixelate":
        return pixelate(image, options.get("size", 32))

    if operation == "sharpen_resize":
        return sharpen_and_resize(image, options.get("size", 64))

    if operation in ("add", "subtract"):
        return add_or_subtract(image, image2, operation)

    if operation == "noise":
        return add_noise(
            image,
            options.get("strength", 20),
            options.get("noise_type", "gaussian")
        )

    if operation == "blur":
        return image.convert("RGB").filter(
            ImageFilter.GaussianBlur(radius=2)
        )

    if operation == "sharpen":
        return image.convert("RGB").filter(ImageFilter.SHARPEN)

    if operation == "pipeline":
        operations = options.get("operations", [])
        result = image.convert("RGB")

        for step in operations:
            if step in ("grayscale", "sketch", "blur", "sharpen"):
                result = apply_operation(result, step)
            elif step in ("pixelate", "sharpen_resize", "noise"):
                result = apply_operation(result, step, options=options)

        return result

    raise ValueError("Unsupported image operation.")
