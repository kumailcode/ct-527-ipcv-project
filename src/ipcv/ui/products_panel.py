"""
Similar Products section: placeholder grid and recommendation thumbnails.
"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from PIL import Image

from ipcv import config
from ipcv.logging_config import get_logger
from ipcv.ui.widgets.dashed_frame import DashedFrame
from ipcv.ui.widgets.divider import add_divider

logger = get_logger("ui.products_panel")


class ProductsPanel(ctk.CTkFrame):
    """
    Bottom panel that lists up to five visually similar catalog items.

    Shows an italic hint when empty; after a successful search, renders
    150x150 thumbnails loaded from dataset paths.
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color=config.COLOR_PAGE_BG, **kwargs)
        self._card_frames: list[ctk.CTkFrame] = []
        self._card_labels: list[ctk.CTkLabel] = []
        self._card_images: list[ctk.CTkImage | None] = []
        self._status_label: ctk.CTkLabel | None = None
        self._build()

    def _build(self) -> None:
        """Build heading, status label, divider, and dashed card container."""
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(
            fill="x",
            padx=config.PAD_SECTION_X,
            pady=(config.PAD_SECTION_Y // 2, config.PAD_SECTION_Y // 2),
        )

        title_row = ctk.CTkFrame(header_row, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(
            title_row,
            text="Similar Products",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=config.COLOR_PRIMARY,
            anchor="w",
        ).pack(side="left")

        self._status_label = ctk.CTkLabel(
            title_row,
            text="",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=config.COLOR_PLACEHOLDER_HINT,
        )
        self._status_label.pack(side="left", padx=(12, 0))

        add_divider(self)

        self._dashed = DashedFrame(self)
        self._dashed.pack(
            fill="both",
            expand=True,
            padx=config.PAD_SECTION_X,
            pady=(config.PAD_SECTION_Y // 2, config.PAD_SECTION_Y),
        )

        self._content = self._dashed.content
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

        self._empty_label = ctk.CTkLabel(
            self._content,
            text=config.EMPTY_PRODUCTS_HINT,
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color=config.COLOR_PLACEHOLDER_HINT,
        )
        self._empty_label.place(relx=0.5, rely=0.5, anchor="center")

        self._cards_frame = ctk.CTkFrame(self._content, fg_color=config.COLOR_PAGE_BG)
        self._build_product_cards()

    def _build_product_cards(self) -> None:
        """Allocate five fixed-size card frames in a horizontal row."""
        for index in range(config.PRODUCT_CARD_COUNT):
            card = ctk.CTkFrame(
                self._cards_frame,
                width=config.PRODUCT_CARD_SIZE,
                height=config.PRODUCT_CARD_SIZE,
                fg_color=config.COLOR_PLACEHOLDER,
                corner_radius=10,
                border_width=1,
                border_color=config.COLOR_PRODUCT_BORDER,
            )
            card.pack(
                side="left",
                padx=config.GAP_PRODUCT_CARDS // 2,
                pady=config.PAD_SECTION_Y,
            )
            card.pack_propagate(False)

            label = ctk.CTkLabel(
                card,
                text="",
                width=config.PRODUCT_CARD_SIZE,
                height=config.PRODUCT_CARD_SIZE,
            )
            label.place(relx=0.5, rely=0.5, anchor="center")

            self._card_frames.append(card)
            self._card_labels.append(label)
            self._card_images.append(None)

        logger.debug("Created %d product card slots", config.PRODUCT_CARD_COUNT)

    def set_status(self, message: str) -> None:
        """
        Update the inline status text (e.g. while searching).

        Args:
            message: Text beside the section title; empty string hides it.
        """
        if self._status_label is not None:
            self._status_label.configure(text=message)
            if message:
                logger.info("Products status: %s", message)

    def set_has_query_image(self, has_image: bool) -> None:
        """
        Toggle between the empty-state hint and the card row layout.

        Args:
            has_image: True after the user uploads a query image.
        """
        if has_image:
            logger.debug("Showing product card row")
            self._empty_label.place_forget()
            self._cards_frame.place(relx=0.5, rely=0.5, anchor="center")
        else:
            logger.debug("Showing empty-state hint")
            self._cards_frame.place_forget()
            self._empty_label.place(relx=0.5, rely=0.5, anchor="center")

    def clear_recommendations(self) -> None:
        """Remove all thumbnails and reset status text."""
        logger.debug("Clearing recommendation thumbnails")
        self.set_status("")
        for label in self._card_labels:
            label.configure(image=None)
        self._card_images = [None] * len(self._card_labels)

    def set_recommendations(self, image_paths: list[Path]) -> None:
        """
        Populate card slots with thumbnails for the recommended paths.

        Args:
            image_paths: Up to five absolute paths under ``data/dataset/``.
        """
        logger.info("Rendering %d recommendation thumbnails", len(image_paths))
        self.set_status("")
        self.clear_recommendations()

        for index, label in enumerate(self._card_labels):
            if index >= len(image_paths):
                break
            thumbnail = self._load_thumbnail(image_paths[index])
            if thumbnail is None:
                logger.warning("Thumbnail failed for slot %d: %s", index + 1, image_paths[index])
                continue
            ctk_image = ctk.CTkImage(
                light_image=thumbnail,
                dark_image=thumbnail,
                size=thumbnail.size,
            )
            self._card_images[index] = ctk_image
            label.configure(image=ctk_image)
            logger.info("Slot %d: %s", index + 1, image_paths[index].name)

    @staticmethod
    def _load_thumbnail(path: Path) -> Image.Image | None:
        """
        Open an image file and resize it for a product card.

        Args:
            path: Catalog image path.

        Returns:
            PIL RGBA image, or None on I/O error.
        """
        try:
            image = Image.open(path).convert("RGBA")
            image.thumbnail(
                (config.PRODUCT_CARD_SIZE, config.PRODUCT_CARD_SIZE),
                Image.Resampling.LANCZOS,
            )
            return image
        except OSError:
            return None
