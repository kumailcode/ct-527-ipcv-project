"""
Horizontal section divider matching the UI design specification.
"""

import customtkinter as ctk

from ipcv import config


def add_divider(parent: ctk.CTkFrame, padx: int = config.PAD_SECTION_X) -> ctk.CTkFrame:
    """
    Pack a full-width horizontal rule below or above a section.

    Args:
        parent: Container frame that will own the divider.
        padx: Horizontal padding in pixels.

    Returns:
        The ``CTkFrame`` widget acting as the divider (fixed 2px height).
    """
    divider = ctk.CTkFrame(
        parent,
        height=config.DIVIDER_HEIGHT,
        fg_color=config.COLOR_BORDER,
        corner_radius=0,
        border_width=0,
    )
    divider.pack(fill="x", padx=padx, pady=0)
    divider.pack_propagate(False)
    return divider
