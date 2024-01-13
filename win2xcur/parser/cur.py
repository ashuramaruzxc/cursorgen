import io
import struct
from PIL import Image
from typing import List

from win2xcur.cursor import CursorFrame, CursorImage
from win2xcur.parser.base import BaseParser


class CURParser(BaseParser):
    MAGIC = b'\0\0\02\0'
    ICO_TYPE_CUR = 2
    ICON_DIR = struct.Struct('<HHH')
    ICON_DIR_ENTRY = struct.Struct('<BBBBHHII')

    @classmethod
    def can_parse(cls, blob: bytes) -> bool:
        return blob[:len(cls.MAGIC)] == cls.MAGIC

    def __init__(self, blob: bytes) -> None:
        super().__init__(blob)
        self.image_data: List[bytes] = []
        self._hotspots = self._parse()
        self.frames = self._create_frames()

    def _parse(self) -> [list[tuple[int, int]]]:
        reserved, ico_type, image_count = self.ICON_DIR.unpack(self.blob[:self.ICON_DIR.size])
        assert reserved == 0
        assert ico_type == self.ICO_TYPE_CUR

        offset = self.ICON_DIR.size
        hotspots = []
        for i in range(image_count):
            width, height, palette, reserved, hx, hy, size, file_offset = self.ICON_DIR_ENTRY.unpack(
                self.blob[offset:offset + self.ICON_DIR_ENTRY.size])
            self.image_data.append(self.blob[:file_offset + size])
            hotspots.append((hx, hy))

            offset += self.ICON_DIR_ENTRY.size

        return hotspots

    def _create_frames(self) -> List[CursorFrame]:
        images = []
        for hotspot, image_data in zip(self._hotspots, self.image_data):
            png_data = self._to_png(image_data)

            stream = io.BytesIO(png_data)

            image = Image.open(stream)
            image.load()
            stream.close()
            c_image = CursorImage(image, hotspot, image.width)
            images.append(c_image)
        return [CursorFrame(images)]

    @staticmethod
    def _to_bmp(blob: bytes) -> bytes:
        bmp_header_size = 14
        dib_header_size = struct.unpack_from('<I', blob[:4])[0]

        original_height = struct.unpack_from('<I', blob[8:12])[0]
        corrected_height = original_height // 2

        # Adjust file size in BMP header
        file_size = bmp_header_size + len(blob) - (corrected_height * 4)  # Assuming 32bpp for simplicity
        pixel_data_offset = bmp_header_size + dib_header_size

        # Create a corrected DIB header with the new height
        corrected_dib_header = blob[:8] + struct.pack('<I', corrected_height) + blob[12:dib_header_size]

        # Construct the BMP header
        bmp_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, pixel_data_offset)
        header = bytes(bmp_header + corrected_dib_header + blob[dib_header_size:])

        return header

    @staticmethod
    def _to_png(blob: bytes) -> bytes:
        # Convert CUR image data to PNG format.
        with io.BytesIO(blob) as input_stream:
            with Image.open(input_stream) as img:
                with io.BytesIO() as output_stream:
                    img.save(output_stream, format="PNG")
                    return output_stream.getvalue()
