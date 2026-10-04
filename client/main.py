"""Flet application entry point.

Start with ``flet run client/main.py``.
"""

from __future__ import annotations

import flet as ft
from client.app import main


if __name__ == "__main__":
    ft.run(main)
