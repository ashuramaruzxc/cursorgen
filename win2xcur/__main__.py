import argparse
import os
import sys
import traceback
from multiprocessing import cpu_count

from multiprocessing.pool import ThreadPool
from threading import Lock
from typing import BinaryIO

from win2xcur.utils import scale
from win2xcur.parser import open_blob
from win2xcur.writer import to_x11


def main() -> None:
    parser = argparse.ArgumentParser(description='Converts Windows cursors to X11 cursors.')
    parser.add_argument('files', type=argparse.FileType('rb'), nargs='+',
                        help='Windows cursor files to convert (*.cur, *.ani)')
    parser.add_argument('-o', '--output', '--output-dir', default=os.curdir,
                        help='Directory to store converted cursor files.')
    parser.add_argument('--scale', default=None, type=float,
                        help='Scale the cursor by the specified factor.')

    args = parser.parse_args()
    print_lock = Lock()

    def process(file: BinaryIO) -> None:
        name = file.name
        blob = file.read()
        try:
            cursor = open_blob(blob)
        except Exception:
            with print_lock:
                print(f'Error occurred while processing {name}:', file=sys.stderr)
                traceback.print_exc()
        else:
            if args.scale:
                scale.apply_to_frames(cursor.frames, scale=args.scale)
            result = to_x11(cursor.frames)
            output = os.path.join(args.output, os.path.splitext(os.path.basename(name))[0])

            with open(f"{output}", 'wb') as f:
                f.write(result)

    with ThreadPool(cpu_count()) as pool:
        pool.map(process, args.files)


if __name__ == '__main__':
    main()
