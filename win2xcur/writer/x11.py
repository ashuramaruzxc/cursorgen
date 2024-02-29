from itertools import chain
from operator import itemgetter
from typing import Any, List, Optional
import numpy as np

from PIL import Image
from win2xcur.cursor import CursorFrame
from win2xcur.parser import XCursorParser

SIZES = [22, 24, 28, 32, 36, 40, 48, 56, 64, 72, 80, 88, 96]


def premultiply_alpha(image: Image.Image) -> Image.Image:
    """
    Premultiply the alpha channel of the image.
    This function assumes the image is in RGBA mode.
    """
    np_image = np.array(image)
    if np_image.ndim != 3:
        raise ValueError("Image must be in RGBA mode with 3 dimensions")

    # Separate the alpha channel and normalize it
    alpha_layer = np_image[:, :, 3] / 255.0

    # Premultiply the RGB channels by the alpha channel
    np_image[:, :, :3] = (np_image[:, :, :3] * alpha_layer[:, :, None]).astype(np.uint8)
    return Image.fromarray(np_image, 'RGBA')


def transform(image: Image.Image) -> Image.Image:
    # Ensure the image is in RGBA mode
    image = image.convert('RGBA')

    # Remove the black background
    data = np.array(image)
    red, green, blue, alpha = data.T
    black_areas = (red == 0) & (blue == 0) & (green == 0)
    data[..., :-1][black_areas.T] = (255, 255, 255)  # Set those pixels to white
    data[..., -1][black_areas.T] = 0  # Set full transparency

    # Convert back to Image and premultiply alpha
    return premultiply_alpha(Image.fromarray(data))


def to_x11(frames: List[CursorFrame], sizes: Optional[List[int]] = None) -> bytes:
    if not sizes:
        sizes = set(SIZES)
    else:
        sizes = set(sizes)

    chunks = []
    for frame in frames:
        for cursor in frame:
            hx, hy = cursor.hotspot
            delay = int(frame.delay * 1000)
            image = cursor.image
            width, height = image.width, image.height
            for size in sizes:
                scale_factor = size / max(width, height)
                x, y = (int(hx * scale_factor), int(hy * scale_factor))

                if image.mode != "RGBA":
                    image = image.convert("RGBA")

                new_image = image.resize((size, size), Image.Resampling.NEAREST)

                alpha = transform(new_image)
                image_data = alpha.tobytes("raw", "BGRA")

                header = XCursorParser.IMAGE_HEADER.pack(
                    XCursorParser.IMAGE_HEADER.size,
                    XCursorParser.CHUNK_IMAGE,
                    size,
                    1,
                    size,
                    size,
                    x,
                    y,
                    delay,
                )
                chunks.append((
                    XCursorParser.CHUNK_IMAGE,
                    size,
                    header + image_data
                ))

    header = XCursorParser.FILE_HEADER.pack(
        XCursorParser.MAGIC,
        XCursorParser.FILE_HEADER.size,
        XCursorParser.VERSION,
        len(chunks),
    )

    offset = XCursorParser.FILE_HEADER.size + len(chunks) * XCursorParser.TOC_CHUNK.size
    toc = []
    for chunk_type, chunk_subtype, chunk in chunks:
        toc.append(XCursorParser.TOC_CHUNK.pack(
            chunk_type,
            chunk_subtype,
            offset,
        ))
        offset += len(chunk)

    return b''.join(chain([header], toc, map(itemgetter(2), chunks)))
