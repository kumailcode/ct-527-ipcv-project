"""
Dashed-border container used for upload and results areas in the UI mockups.
"""

import tkinter as tk

import customtkinter as ctk

from ipcv import config


class DashedFrame(ctk.CTkFrame):
    """
    ``CTkFrame`` with a dashed rectangle drawn on an underlying ``tk.Canvas``.

    Inner widgets are placed in ``self.content``, inset so the border remains
    visible after resize.
    """

    def __init__(
        self,
        master,
        border_color: str = config.COLOR_DASHED_BORDER,
        dash: tuple[int, int] = (8, 4),
        inset: int = config.PAD_DASHED_INSET,
        **kwargs,
    ) -> None:
        kwargs.setdefault("fg_color", config.COLOR_PAGE_BG)
        super().__init__(master, **kwargs)

        self._border_color = border_color
        self._dash = dash
        self._inset = inset

        self._canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bd=0,
            bg=config.COLOR_PAGE_BG,
        )
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.content = ctk.CTkFrame(self, fg_color=config.COLOR_PAGE_BG)
        self.content.pack(
            fill="both",
            expand=True,
            padx=inset,
            pady=inset,
        )

        self.bind("<Configure>", self._redraw_border)
        self.after_idle(self._redraw_border)

    def _redraw_border(self, _event=None) -> None:
        """Redraw the dashed outline when this frame is resized."""
        self._canvas.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 4 or height < 4:
            return

        pad = 4
        self._canvas.create_rectangle(
            pad,
            pad,
            width - pad,
            height - pad,
            outline=self._border_color,
            width=1,
            dash=self._dash,
        )
