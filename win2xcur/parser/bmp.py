import struct
from typing import List, Optional, Tuple, Any

from win2xcur.parser.base import BaseParser


class BMPParser(BaseParser):
    SIGNATURE = {
        b'BM': 'Windows BMP',
        b'BA': 'OS/2 Bitmap Array',
        b'CI': 'OS/2 Color Icon',
        b'CP': 'OS/2 Color Pointer',
        b'IC': 'OS/2 Icon',
        b'PT': 'OS/2 Pointer'
    }
    # Signature
    # FileSize
    # Reserved1
    # Reserved2
    # offbits
    BMP_HEADER = struct.Struct('<2sIHHI')
    # DIB header (BITMAPINFOHEADER)
    DIB_HEADER = struct.Struct('<IIIHHIIIIII')

    @classmethod
    def can_parse(cls, blob: bytes) -> bool:
        """Check if the blob is one of the supported BMP types."""
        if len(blob) < cls.BMP_HEADER.size:
            return False
        signature, *_ = cls.BMP_HEADER.unpack_from(blob)
        return signature in cls.SIGNATURE

    def __init__(self, blob: bytes) -> None:
        self.blob = blob
        self.image_type = self._get_image_type(blob)
        # if not self.image_type:
        #     raise ValueError(f"Not a valid BMP file or unsupported BMP type, expected:{self.image_type}")
        self.width, self.height, self.bits_per_pixel = self._parse()

    def _unpack(self, struct_cls: struct.Struct, offset: int) -> Tuple[Any, ...]:
        return struct_cls.unpack(self.blob[offset:offset + struct_cls.size])

    def _parse(self) -> Tuple[int, int, int]:
        signature, size, reserved1, reserved2, offset = self.BMP_HEADER.unpack(self.blob[:self.BMP_HEADER.size])
        assert reserved1 == 0
        assert reserved2 == 0

    def _get_image_type(self, blob: bytes) -> Optional[str]:
        """Identify the BMP image type based on its signature."""
        if len(blob) < self.BMP_HEADER.size:
            return None
        signature, *_ = self.BMP_HEADER.unpack_from(blob)
        return self.SIGNATURE.get(signature)

    def _parse_dib_headers(self):
        offset = self.BMP_HEADER.size

        off_img, size = self.BMP_HEADER.unpack(
            self.blob[offset:offset + self.BMP_HEADER.size])

        if size == 40:
            return self._parse_bitmapinfoheader(offset)
        elif size == 108:
            return self._parse_bitmapv4header(offset)
        elif size == 124:
            return self._parse_bitmapv5header(offset)
        else:
            raise ValueError(f"Unsupported DIB header size: {size}")

    def _parse_bitmapinfoheader(self, offset: int) -> Tuple[int, int, int, int]:
        size, width, height, planes, bits_per_pixel, compression, image_size, x_pixels_per_meter, y_pixels_per_meter, colors_used, important_colors = self.DIB_HEADER.unpack_from(
            self.blob, offset)
        return width, abs(height), bits_per_pixel, compression

    def _parse_bitmapv4header(self, offset) -> Tuple[int, int, int, int]:
        size, width, height, planes, bits_per_pixel, compression, image_size, x_pixels_per_meter, y_pixels_per_meter, colors_used, important_colors = self.DIB_HEADER.unpack_from(
            self.blob, offset)
        return width, abs(height), bits_per_pixel, compression

    def _parse_bitmapv5header(self, offset) -> Tuple[int, int, int, int]:
        size, width, height, planes, bits_per_pixel, compression, image_size, x_pixels_per_meter, y_pixels_per_meter, colors_used, important_colors = self.DIB_HEADER.unpack_from(
            self.blob, offset)
        return width, abs(height), bits_per_pixel, compression

    def _extract_pixel_data(self, width, height, bpp, offset):
        """Extracts pixel data from a BMP file.

        Args:
            width (int): The width of the image.
            height (int): The height of the image.
            bpp (int): Bits per pixel.
            offset (int): The offset where pixel data starts in the blob.

        Returns:
            A 2D array of pixels.
        """
        # Calculate the number of bytes per pixel
        bytes_per_pixel = bpp // 8

        # BMP rows are padded to 4 bytes
        row_padded = (width * bytes_per_pixel + 3) & ~3

        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel_offset = offset + y * row_padded + x * bytes_per_pixel
                pixel_data = self.blob[pixel_offset:pixel_offset + bytes_per_pixel]
                # Assuming the BMP uses BGRA format, convert to RGBA or as needed
                if bytes_per_pixel == 3:  # For 24bpp
                    pixel = (pixel_data[2], pixel_data[1], pixel_data[0])  # Convert BGR to RGB
                elif bytes_per_pixel == 4:  # For 32bpp
                    pixel = (pixel_data[2], pixel_data[1], pixel_data[0], pixel_data[3])  # Convert BGRA to RGBA
                else:
                    raise ValueError("Unsupported bits per pixel")
                row.append(pixel)
            pixels.append(row)

        return pixels
