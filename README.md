# `cursorgen`

`cursorgen` is a fork of [win2xcur](https://github.com/quantum5/win2xcur) that aims to preserve the image quality of
the cursor by converting cursror frames to Bitmap format in order to preserve the original palette colors and shadows.
It also rewrites some functionality of win2xcur from wand to Pillow in order to not rely on imagemagick and simplicity of it.

## Installation

To install the latest stable version:

    pip install cursorgen

## Usage: `cursorgen`

For example, if you want to convert [the sample cursor](sample/crosshair.cur)
to Linux format:

    mkdir output/
    cursorgen sample/crosshair.cur -o output/

For more information, run `cursorgen --help`.
