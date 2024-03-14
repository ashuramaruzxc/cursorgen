import struct
from typing import Any, Dict, List, Tuple

import PIL.Image as ImageType
from PIL import Image

from cursorgen.parser.base import BaseParser


class BMPParser(BaseParser):
    """adapted parts of:
    https://chromium.googlesource.com/chromium/src/+/master/tools/resources/ico_tools.py
    https://github.com/SystemRage/Iconolatry/blob/master/Iconolatry.py
    """

    BMP_HEADER = struct.Struct("<2sIHHI")
    DIB_HEADER = struct.Struct("<IIIHHIIIIII")

    @classmethod
    def can_parse(cls, blob: bytes) -> bool:
        """Check if the blob is one of the supported BMP types."""
        if len(blob) < cls.BMP_HEADER.size:
            return False
        signature: bool = cls.BMP_HEADER.unpack_from(blob)[0]
        return signature

    def __init__(self, blob: bytes) -> None:
        super().__init__(blob)
        self.image_data: List[bytes] = []
        self.parameters = self._extract()
        self.frame = self._parse()

    def _unpack(self, struct_cls: struct.Struct, offset: int) -> Tuple[Any, ...]:
        return struct_cls.unpack(self.blob[offset : offset + struct_cls.size])

    def _extract(self) -> Dict[str, Any]:
        """Gets bitmap parameters.
        Should be:
        biSize is the size of the header
        biHeight doubled respect bHeight
        biPlanes = 1
        biCompression = 0 (if BI_RGB)
        biSizeImage = size of the XOR mask + AND mask (can be also 0)
        biXPPerMeter = 0 (if not used)
        biYPPerMeter = 0 (if not used)
        biClrUsed = 0 (if not used)
        biClrImportant = 0 (if not used)
        """
        (
            size,
            width,
            height,
            planes,
            bpp,
            compression,
            image_size,
            x_pixels_per_meter,
            y_pixels_per_meter,
            colors_used,
            important_colors,
        ) = self.DIB_HEADER.unpack(self.blob[: self.DIB_HEADER.size])

        height = int(height / 2.0)

        XOR_size = self._row_size(bpp, width) * height
        AND_size = self._mask_size(width) * height

        palette_size = len(self.blob) - (size + XOR_size + AND_size)
        if palette_size < 0:
            palette_size = 0

        Palette = self.blob[size : size + palette_size]
        XORData = self.blob[size + palette_size : size + palette_size + XOR_size]
        ANDData = self.blob[size + palette_size + XOR_size : len(self.blob)]

        parameters = {
            "size": size,
            "width": width,
            "height": height,
            "planes": planes,
            "bpp": bpp,
            "compress": compression,
            "size_img": image_size,
            "colors": colors_used,
            "size_pal": palette_size,
            "num_pal": 0,
            "palette": Palette,
            "size_xor": XOR_size,
            "xor": XORData,
            "size_and": AND_size,
            "and": ANDData,
        }
        return parameters

    def _parse(self) -> ImageType:
        """Gets image from bytes."""

        modes = {
            32: ("RGBA", "BGRA"),
            24: ("RGB", "BGR"),
            16: ("RGB", "BGR"),
            8: ("P", "P"),
            4: ("P", "P;4"),
            2: ("P", "P;2"),
            1: ("P", "P;1"),
        }

        if self.is_gray():
            modes.update(
                {8: ("L", "L"), 4: ("L", "L;4"), 2: ("L", "L;2"), 1: ("1", "1")}
            )

        pad_msk = self._mask_size(self.parameters["width"])

        if self.parameters["bpp"] == 16:
            # PIL I;16 converted to RGB555 format.
            pad_ima = self._row_size(24, self.parameters["width"])
            images_data = []
            for i in range(0, len(self.parameters["xor"]), 2):
                data = int.from_bytes(
                    self.parameters["xor"][i : i + 2], byteorder="little"
                )
                b = (data & 0x7C00) >> 10
                g = (data & 0x3E0) >> 5
                r = data & 0x1F
                r = (r << 3) | (r >> 2)
                g = (g << 3) | (g >> 2)
                b = (b << 3) | (b >> 2)
                value = r << 16 | g << 8 | b
                images_data.append(value.to_bytes(3, byteorder="little"))

            image_data = b"".join(images_data)
            image = Image.frombytes(
                modes[self.parameters["bpp"]][0],
                (self.parameters["width"], self.parameters["height"]),
                image_data,
                "raw",
                modes[self.parameters["bpp"]][1],
                pad_ima,
                -1,
            )
        else:
            pad_ima = self._row_size(self.parameters["bpp"], self.parameters["width"])
            image = Image.frombytes(
                modes[self.parameters["bpp"]][0],
                (self.parameters["width"], self.parameters["height"]),
                self.parameters["xor"],
                "raw",
                modes[self.parameters["bpp"]][1],
                pad_ima,
                -1,
            )

        if self.parameters["bpp"] == 32:
            mask = Image.frombuffer(
                "L",
                (self.parameters["width"], self.parameters["height"]),
                self.parameters["xor"][3::4],
                "raw",
                "L",
                0,
                -1,
            )
        else:
            mask = Image.frombuffer(
                "1",
                (self.parameters["width"], self.parameters["height"]),
                self.parameters["and"],
                "raw",
                "1;I",
                pad_msk,
                -1,
            )

        if self.parameters["palette"] and self.parameters["bpp"] <= 8:
            image = image.convert("P")
            palette_int = [
                self.parameters["palette"][i : i + 3]
                for i in range(0, self.parameters["size_pal"], 4)
            ]
            rsv = [
                self.parameters["palette"][i + 3 : i + 4]
                for i in range(0, self.parameters["size_pal"], 4)
            ]

            if (self.parameters["size_pal"] % 3 == 0) and (
                self.parameters["size_pal"] % 4 == 0
            ):
                if len(set(rsv)) <= 1:
                    # palette RGBA.
                    palette_int = [
                        pal[i] for pal in palette_int for i in reversed(range(3))
                    ]
                    self.parameters["num_pal"] = self.parameters["size_pal"] // 4
                else:
                    # palette RGB.
                    palette_int = [pal for pal in self.parameters["palette"][::-1]]
                    self.parameters["num_pal"] = self.parameters["size_pal"] // 3
            else:
                if self.parameters["size_pal"] % 3 == 0:
                    # palette RGB.
                    palette_int = [pal for pal in self.parameters["palette"][::-1]]
                    self.parameters["num_pal"] = self.parameters["size_pal"] // 3
                elif self.parameters["size_pal"] % 4 == 0:
                    # palette RGBA.
                    palette_int = [
                        pal[i] for pal in palette_int for i in reversed(range(3))
                    ]
                    self.parameters["num_pal"] = self.parameters["size_pal"] // 4

            if self.parameters["bpp"] == 1:
                pal = list(image.palette.getdata()[1])
                pal[:3], pal[-3:] = palette_int[:3], palette_int[-3:]
                palette_int = pal
            # Assign palette.
            image.putpalette(palette_int)

        image = image.convert("RGBA")
        image.putalpha(mask)

        return image

    @staticmethod
    def _row_size(offset: int, width: int) -> int:
        """Computes number of bytes per row in a image (stride)."""
        # The size of each row is rounded up to the nearest multiple of 4 bytes.
        return int(((offset * width + 31) // 32)) * 4

    @staticmethod
    def _mask_size(width: int) -> int:
        """Computes number of bytes for AND mask."""
        return int((width + 32 - width % 32 if (width % 32) > 0 else width) / 8)

    @staticmethod
    def is_png(blob: bytes) -> bool:
        """Determines whether a sequence of bytes is a PNG."""
        return blob.startswith(b"\x89PNG\r\n\x1a\n")

    def is_gray(self) -> bool:
        """Determines whether an image is grayscale (from palette)."""
        chunks = [
            self.parameters["palette"][i : i + 3]
            for i in range(0, self.parameters["size_pal"], 4)
        ]
        if all(elem == block[0] for block in chunks for elem in block):
            return True
        else:
            return False
