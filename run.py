#!/usr/bin/env python3
"""
Launcher for the Visual Recommender System desktop application.

Adds ``src/`` to ``sys.path`` so the ``ipcv`` package imports without installation.
Run from the project root with the virtual environment activated:

    python run.py
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ipcv.app import run  # noqa: E402

if __name__ == "__main__":
    run()
