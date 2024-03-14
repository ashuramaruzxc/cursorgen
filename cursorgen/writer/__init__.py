from cursorgen.writer.x11 import to_x11

__all__ = ["to_x11"]

CONVERTERS = {
    "x11": (to_x11, ""),
}
