"""
Upload and preview panel for the user's query product image.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk
from PIL import Image
from tkinter import filedialog

from ipcv import config
from ipcv.logging_config import get_logger
from ipcv.ui.widgets.dashed_frame import DashedFrame
from ipcv.ui.widgets.divider import add_divider

logger = get_logger("ui.upload_panel")


class UploadPanel(ctk.CTkFrame):
    """
    Central workspace for selecting, previewing, and clearing the query image.

    Empty state shows only an Upload button. Loaded state shows a 150x150
    preview and a Clear button that triggers ``on_image_changed(None)``.
    """

    def __init__(
        self,
        master,
        on_image_changed: Optional[Callable[[Optional[Path]], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color=config.COLOR_PAGE_BG, **kwargs)
        self._on_image_changed = on_image_changed
        self._current_path: Optional[Path] = None
        self._preview_ctk_image: Optional[ctk.CTkImage] = None
        self._build()

    def _build(self) -> None:
        """Construct dashed container, preview frame, and action button."""
        self._dashed = DashedFrame(self)
        self._dashed.pack(
            fill="both",
            expand=True,
            padx=config.PAD_SECTION_X,
            pady=(config.PAD_SECTION_Y, config.PAD_SECTION_Y // 2),
        )

        body = self._dashed.content
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        center = ctk.CTkFrame(body, fg_color=config.COLOR_PAGE_BG)
        center.grid(row=0, column=0, sticky="nsew")
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=1)

        self._stack = ctk.CTkFrame(center, fg_color=config.COLOR_PAGE_BG)
        self._stack.place(relx=0.5, rely=0.5, anchor="center")

        self._preview_box = ctk.CTkFrame(
            self._stack,
            width=config.PREVIEW_SIZE,
            height=config.PREVIEW_SIZE,
            fg_color=config.COLOR_PLACEHOLDER,
            corner_radius=8,
        )
        self._preview_box.grid(row=0, column=0)
        self._preview_box.grid_propagate(False)

        self._preview_label = ctk.CTkLabel(
            self._preview_box,
            text="",
            width=config.PREVIEW_SIZE,
            height=config.PREVIEW_SIZE,
        )
        self._preview_label.place(relx=0.5, rely=0.5, anchor="center")

        self._action_btn = ctk.CTkButton(
            self._stack,
            text="Upload",
            width=140,
            height=36,
            corner_radius=18,
            fg_color=config.COLOR_PRIMARY,
            hover_color="#005091",
            command=self._on_action_clicked,
        )
        self._action_btn.grid(
            row=1,
            column=0,
            pady=(config.GAP_PREVIEW_TO_BUTTON, 0),
        )

        add_divider(self)
        self._show_empty_state()
        logger.debug("Upload panel built")

    def _show_empty_state(self) -> None:
        """Show only the Upload button inside the dashed region."""
        self._preview_box.grid_remove()
        self._action_btn.configure(text="Upload")
        self._action_btn.grid(row=0, column=0, pady=0)

    def _show_loaded_state(self) -> None:
        """Show preview thumbnail with Clear button below."""
        self._preview_box.grid(row=0, column=0)
        self._action_btn.configure(text="Clear")
        self._action_btn.grid(
            row=1,
            column=0,
            pady=(config.GAP_PREVIEW_TO_BUTTON, 0),
        )

    def _on_action_clicked(self) -> None:
        """Open file dialog for upload, or clear the current selection."""
        if self._current_path is None:
            self._pick_image()
        else:
            self.clear_image()

    def _pick_image(self) -> None:
        """Display the native file picker and load the chosen image."""
        logger.info("Opening file picker for query image")
        file_path = filedialog.askopenfilename(
            title="Select product image",
            filetypes=config.IMAGE_FILE_TYPES,
        )
        if not file_path:
            logger.info("File picker cancelled")
            return
        self.set_image(Path(file_path))

    def set_image(self, path: Path) -> None:
        """
        Render a thumbnail preview and notify the main window.

        Args:
            path: Absolute path to the selected image file.
        """
        logger.info("Loading preview for %s", path)
        try:
            pil_image = Image.open(path).convert("RGBA")
        except OSError as exc:
            logger.error("Could not open image: %s", exc)
            return

        pil_image.thumbnail(
            (config.PREVIEW_SIZE, config.PREVIEW_SIZE),
            Image.Resampling.LANCZOS,
        )
        self._preview_ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=pil_image.size,
        )
        self._preview_label.configure(image=self._preview_ctk_image)
        self._current_path = path
        self._show_loaded_state()
        logger.info("Preview displayed (%dx%d)", pil_image.width, pil_image.height)

        if self._on_image_changed:
            self._on_image_changed(path)

    def clear_image(self) -> None:
        """Remove preview and notify listeners with ``None``."""
        logger.info("Clearing query image")
        self._current_path = None
        self._preview_ctk_image = None
        self._preview_label.configure(image=None)
        self._show_empty_state()

        if self._on_image_changed:
            self._on_image_changed(None)

    @property
    def current_image_path(self) -> Optional[Path]:
        """Currently selected query image, or ``None`` if empty."""
        return self._current_path
