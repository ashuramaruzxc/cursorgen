import io
from itertools import chain
from operator import itemgetter
from typing import List, Optional

from PIL import Image
from win2xcur.cursor import CursorFrame
from win2xcur.parser import XCursorParser

SIZES = [22, 24, 28, 32, 36, 40, 48, 56, 64, 72, 80, 88, 96]


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

                new_image = image.resize((size, size), Image.Resampling.NEAREST)
                blob = io.BytesIO()
                new_image.save(blob, "PNG", optimize=True)
                image_data = blob.getvalue()

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
