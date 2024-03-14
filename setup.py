import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    long_description = f.read()

setup(
    name="cursorgen",
    version="0.1.2",
    packages=find_packages(),
    install_requires=["numpy", "pillow"],
    entry_points={
        "console_scripts": [
            "cursorgen = cursorgen.__main__:main",
        ],
    },
    author="ashuramaruzxc",
    author_email="ashuramaru@tenjin-dk.com",
    url="https://github.com/ashuramaruzxc/cursorgen",
    description=" cursorgen is a fork of win2xcur that aims to preserve the image quality of the cursor.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="cur ani x11 windows win32 cursor xcursor",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
    ],
)
