from typing import List, Type

from win2xcur.parser.ani import ANIParser
from win2xcur.parser.base import BaseParser
from win2xcur.parser.cur import CURParser

PARSERS: List[Type[BaseParser]] = [CURParser, ANIParser]


def open_blob(blob: bytes) -> BaseParser:
    for parser in PARSERS:
        if parser.can_parse(blob):
            return parser(blob)
    raise ValueError('Unsupported file format')
