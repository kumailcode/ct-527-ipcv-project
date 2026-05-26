"""
Application header with course branding, titles, and logo.
"""

from __future__ import annotations

import customtkinter as ctk

from ipcv import config
from ipcv.assets import load_logo_image
from ipcv.logging_config import get_logger
from ipcv.ui.widgets.divider import add_divider

logger = get_logger("ui.header")


class HeaderPanel(ctk.CTkFrame):
    """
    Top gray bar matching the UI mockups: logo left, centered text stack.

    Displays course code, project title, subtitle, and group member names.
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            fg_color=config.COLOR_HEADER_BG,
            corner_radius=0,
            **kwargs,
        )
        self._logo_image = None
        self._build()

    def _build(self) -> None:
        """Lay out logo and centered labels within a fixed-height content frame."""
        logger.debug("Building header panel")
        content = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=config.HEADER_MIN_HEIGHT,
        )
        content.pack(
            fill="x",
            padx=config.HEADER_PAD_X,
            pady=config.HEADER_PAD_Y,
        )
        content.pack_propagate(False)

        text_stack = ctk.CTkFrame(content, fg_color="transparent")
        text_stack.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            text_stack,
            text=config.COURSE_LABEL,
            font=ctk.CTkFont(size=config.FONT_HEADER_COURSE),
            text_color=config.COLOR_TEXT_MUTED,
        ).pack()

        ctk.CTkLabel(
            text_stack,
            text=config.APP_TITLE,
            font=ctk.CTkFont(size=config.FONT_HEADER_TITLE, weight="bold"),
            text_color=config.COLOR_PRIMARY,
        ).pack()

        ctk.CTkLabel(
            text_stack,
            text=config.SUBTITLE,
            font=ctk.CTkFont(size=config.FONT_HEADER_SUBTITLE, slant="italic"),
            text_color=config.COLOR_TEXT_MUTED,
        ).pack()

        ctk.CTkLabel(
            text_stack,
            text=config.MEMBERS_LABEL,
            font=ctk.CTkFont(size=config.FONT_HEADER_MEMBERS, weight="bold"),
            text_color=config.COLOR_TEXT_MUTED,
        ).pack()

        pil_logo = load_logo_image()
        if pil_logo is not None:
            self._logo_image = ctk.CTkImage(
                light_image=pil_logo,
                dark_image=pil_logo,
                size=(config.LOGO_SIZE, config.LOGO_SIZE),
            )
            ctk.CTkLabel(content, image=self._logo_image, text="").place(
                relx=0.0,
                rely=0.5,
                anchor="w",
            )

        add_divider(self, padx=0)
        logger.debug("Header panel complete")
