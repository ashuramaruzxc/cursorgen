from typing import List
from PIL import Image
from win2xcur.cursor import CursorFrame


def apply_to_frames(frames: List[CursorFrame], *, scale: float) -> None:
    for frame in frames:
        for cursor in frame:
            # Calculate new size
            new_width = int(round(cursor.image.width * scale))
            new_height = int(round(cursor.image.height * scale))
            # Ensure dimensions are not reduced to zero
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            # Resize the image
            cursor.image = cursor.image.resize((new_width, new_height), Image.Resampling.NEAREST)
