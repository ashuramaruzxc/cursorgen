# `win2xcur` [![Build Status](https://img.shields.io/github/actions/workflow/status/quantum5/win2xcur/build.yml)](https://github.com/quantum5/win2xcur/actions) [![PyPI](https://img.shields.io/pypi/v/win2xcur.svg)](https://pypi.org/project/win2xcur/) [![PyPI - Format](https://img.shields.io/pypi/format/win2xcur.svg)](https://pypi.org/project/win2xcur/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/win2xcur.svg)](https://pypi.org/project/win2xcur/)

`win2xcur` is a tool that converts cursors from Windows format (`*.cur`,
`*.ani`) to Xcursor format. This allows Windows cursor themes to be used on
Linux, for example.

## Installation

To install the latest stable version:

    pip install win2xcur

## Usage: `win2xcur`

For example, if you want to convert [the sample cursor](sample/crosshair.cur)
to Linux format:

    mkdir output/
    win2xcur sample/crosshair.cur -o output/

For more information, run `win2xcur --help`.
