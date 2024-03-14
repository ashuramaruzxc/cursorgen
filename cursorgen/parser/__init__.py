from typing import List, Type

from cursorgen.parser.ani import ANIParser
from cursorgen.parser.base import BaseParser
from cursorgen.parser.bmp import BMPParser
from cursorgen.parser.cur import CURParser
from cursorgen.parser.xcursor import XCursorParser

__all__ = [
    "BMPParser",
    "ANIParser",
    "CURParser",
    "XCursorParser",
    "PARSERS",
    "open_blob",
]

PARSERS: List[Type[BaseParser]] = [CURParser, ANIParser, XCursorParser]


def open_blob(blob: bytes) -> BaseParser:
    for parser in PARSERS:
        if parser.can_parse(blob):
            return parser(blob)
    raise ValueError("Unsupported file format")
