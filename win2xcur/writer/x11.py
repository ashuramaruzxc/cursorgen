from itertools import chain
from operator import itemgetter
from typing import Any, List
import numpy as np

from win2xcur.cursor import CursorFrame
from win2xcur.parser import XCursorParser


def premultiply_alpha(source: bytes) -> bytes:
    buffer: np.ndarray[Any, np.dtype[np.double]] = np.frombuffer(
        source, dtype=np.uint8
    ).astype(np.double)
    alpha = buffer[3::4] / 255.0
    buffer[0::4] *= alpha
    buffer[1::4] *= alpha
    buffer[2::4] *= alpha
    return buffer.astype(np.uint8).tobytes()


def to_x11(frames: List[CursorFrame]) -> bytes:
    chunks = []

    for frame in frames:
        for cursor in frame:
            hx, hy = cursor.hotspot
            print(cursor.image)

            header = XCursorParser.IMAGE_HEADER.pack(
                XCursorParser.IMAGE_HEADER.size,
                XCursorParser.CHUNK_IMAGE,
                cursor.nominal,
                1,
                cursor.image.width,
                cursor.image.height,
                hx,
                hy,
                int(frame.delay * 1000),
            )
            chunks.append((
                XCursorParser.CHUNK_IMAGE,
                cursor.nominal,
                header + premultiply_alpha(cursor.image.tobytes("raw", "BGRA"))
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
