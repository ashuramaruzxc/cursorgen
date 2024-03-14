import struct
from typing import List, Tuple

from PIL import Image

from cursorgen.parser.base import BaseParser
from cursorgen.parser.bmp import BMPParser
from cursorgen.utils.cursor import CursorFrame, CursorImage


class CURParser(BaseParser):
    MAGIC = b"\0\0\02\0"
    ICO_TYPE_CUR = 2
    ICON_DIR = struct.Struct("<HHH")
    ICON_DIR_ENTRY = struct.Struct("<BBBBHHII")

    @classmethod
    def can_parse(cls, blob: bytes) -> bool:
        return blob[: len(cls.MAGIC)] == cls.MAGIC

    def __init__(self, blob: bytes) -> None:
        super().__init__(blob)
        self.image_data: List[bytes] = []
        self._hotspots = self._parse()
        self.frames = self._create_frames()

    def _parse(self) -> List[Tuple[int, int]]:
        reserved, ico_type, image_count = self.ICON_DIR.unpack(
            self.blob[: self.ICON_DIR.size]
        )
        assert reserved == 0
        assert ico_type == self.ICO_TYPE_CUR

        offset = self.ICON_DIR.size
        hotspots = []
        for i in range(image_count):
            width, height, palette, reserved, hx, hy, size, file_offset = (
                self.ICON_DIR_ENTRY.unpack(
                    self.blob[offset : offset + self.ICON_DIR_ENTRY.size]
                )
            )
            self.image_data.append(self.blob[file_offset : file_offset + size])
            hotspots.append((hx, hy))

            offset += self.ICON_DIR_ENTRY.size
        return hotspots

    def _create_frames(self) -> List[CursorFrame]:
        images = []
        for hotspot, image_data in zip(self._hotspots, self.image_data):
            try:
                image: Image.Image = BMPParser(image_data).frame
                c_image = CursorImage(image, hotspot, image.width)
                images.append(c_image)
            except IOError as e:
                print(f"Error processing image data: {e}")

        return [CursorFrame(images)]
