"""
Root application window: layout, recommendation orchestration, and UI threading.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import customtkinter as ctk
from tkinter import messagebox

from ipcv import config
from ipcv.logging_config import get_logger
from ipcv.recommendation import RecommenderService
from ipcv.ui.header import HeaderPanel
from ipcv.ui.products_panel import ProductsPanel
from ipcv.ui.upload_panel import UploadPanel

logger = get_logger("ui.main_window")


class MainWindow(ctk.CTk):
    """
    Primary desktop window composing header, upload, and similar-products panels.

    Coordinates asynchronous recommendation when the user uploads an image and
    applies results on the main Tk thread via ``after(0, ...)``.
    """

    def __init__(self) -> None:
        super().__init__()
        logger.info("Constructing main window")

        self.title(config.APP_TITLE)
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.configure(fg_color=config.COLOR_PAGE_BG)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self._products_panel: Optional[ProductsPanel] = None
        self._upload_panel: Optional[UploadPanel] = None
        self._recommender = RecommenderService()
        self._recommendation_token = 0

        self._build_layout()
        self._center_on_screen()
        self._preload_index()

    def _build_layout(self) -> None:
        """Place header (fixed height), upload panel, and products panel in a grid."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        HeaderPanel(self).grid(row=0, column=0, sticky="new")
        logger.debug("Header panel attached")

        self._upload_panel = UploadPanel(self, on_image_changed=self._on_image_changed)
        self._upload_panel.grid(row=1, column=0, sticky="nsew")

        self._products_panel = ProductsPanel(self)
        self._products_panel.grid(row=2, column=0, sticky="nsew")
        logger.debug("Upload and products panels attached")

    def _preload_index(self) -> None:
        """Warm the embedding index in a background thread after the UI is visible."""
        logger.info("Requesting background preload of embedding index")
        self._recommender.initialize_async()

    def _on_image_changed(self, path: Optional[Path]) -> None:
        """
        React to upload or clear events from ``UploadPanel``.

        Args:
            path: Selected image path, or ``None`` when cleared.
        """
        if self._products_panel is None:
            return

        if path is None:
            logger.info("Query image cleared — resetting products section")
            self._recommendation_token += 1
            self._products_panel.set_has_query_image(False)
            self._products_panel.clear_recommendations()
            return

        logger.info("Query image set: %s — starting recommendation", path)
        self._products_panel.set_has_query_image(True)
        self._products_panel.clear_recommendations()
        self._products_panel.set_status("Searching for similar products...")
        self._set_upload_enabled(False)

        token = self._recommendation_token + 1
        self._recommendation_token = token

        self._recommender.recommend_async(
            query_path=path,
            on_success=lambda results: self._on_recommendation_done(
                token, results, None
            ),
            on_error=lambda message: self._on_recommendation_done(token, [], message),
        )

    def _on_recommendation_done(
        self,
        token: int,
        results: list[Path],
        error: Optional[str],
    ) -> None:
        """
        Marshal recommendation results onto the Tk main thread.

        Ignores stale responses if the user cleared the image or uploaded a newer one.
        """
        if token != self._recommendation_token:
            logger.debug("Ignoring stale recommendation callback (token %d)", token)
            return

        def apply() -> None:
            self._set_upload_enabled(True)
            if self._products_panel is None:
                return
            if error:
                logger.error("Recommendation failed: %s", error)
                self._products_panel.set_status("")
                messagebox.showerror("Recommendation error", error, parent=self)
                return
            if not results:
                logger.warning("No similar products returned")
                self._products_panel.set_status("No similar products found.")
                return
            logger.info("Displaying %d recommendations in UI", len(results))
            self._products_panel.set_recommendations(results)

        self.after(0, apply)

    def _set_upload_enabled(self, enabled: bool) -> None:
        """Enable or disable the Upload/Clear button during inference."""
        if self._upload_panel is not None:
            state = "normal" if enabled else "disabled"
            self._upload_panel._action_btn.configure(state=state)
            logger.debug("Upload button state: %s", state)

    def _center_on_screen(self) -> None:
        """Position the window at the center of the primary monitor."""
        self.update_idletasks()
        width = max(config.WINDOW_MIN_WIDTH, self.winfo_width())
        height = max(config.WINDOW_MIN_HEIGHT, self.winfo_height())
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        logger.info("Window geometry: %dx%d at (%d, %d)", width, height, x, y)
