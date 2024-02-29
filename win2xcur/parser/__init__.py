from typing import List, Type, Union, Optional

from win2xcur.parser.ani import ANIParser
from win2xcur.parser.base import BaseParser
from win2xcur.parser.bmp import BMPParser
from win2xcur.parser.cur import CURParser
from win2xcur.parser.png import SinglePNGParser, MultiPNGParser
from win2xcur.parser.xcursor import XCursorParser

__all__ = ['BMPParser', 'ANIParser', 'CURParser', 'XCursorParser', 'SinglePNGParser', 'MultiPNGParser', 'PARSERS', 'open_blob']

PARSERS: List[Type[BaseParser]] = [CURParser, ANIParser, XCursorParser, SinglePNGParser, MultiPNGParser]


def open_blob(
    blob: Union[bytes, List[bytes]],
) -> BaseParser:
    for parser in PARSERS:
        if parser.can_parse(blob):
            return parser(blob)  # type: ignore
    raise ValueError("Unsupported file format")
