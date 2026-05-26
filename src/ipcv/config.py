"""
Application-wide constants: filesystem paths, UI theme, layout, and ML settings.

All modules import from here so paths and presentation values stay consistent.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "data" / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

COLOR_PRIMARY = "#0066B2"
COLOR_HEADER_BG = "#E8E8E8"
COLOR_PAGE_BG = "#FFFFFF"
COLOR_TEXT_MUTED = "#5A5A5A"
COLOR_BORDER = "#B0B0B0"
COLOR_DASHED_BORDER = "#A8A8A8"
COLOR_PLACEHOLDER = "#D3D3D3"
COLOR_PLACEHOLDER_HINT = "#9A9A9A"
COLOR_PRODUCT_BORDER = "#B8C8D8"

APP_TITLE = "Visual Recommender System"
COURSE_LABEL = "CT-527 Image Processing and Computer Vision Course Project"
SUBTITLE = "A CNN-Based Universal Visual Product Recommender System"
MEMBERS_LABEL = (
    "Group Members: Kumail Ali Shaikh (CT-053 2024/25) - "
    "Saifullah Siddiqui (CT-031 2024/25)"
)
EMPTY_PRODUCTS_HINT = "Similar products will appear here..."

WINDOW_MIN_WIDTH = 1360
WINDOW_MIN_HEIGHT = 786
PREVIEW_SIZE = 150
PRODUCT_CARD_COUNT = 5
PRODUCT_CARD_SIZE = 150
SECTION_CORNER_RADIUS = 12
DIVIDER_HEIGHT = 2

LOGO_SIZE = 88
HEADER_MIN_HEIGHT = 114
HEADER_PAD_X = 28
HEADER_PAD_Y = 6
FONT_HEADER_COURSE = 12
FONT_HEADER_TITLE = 24
FONT_HEADER_SUBTITLE = 14
FONT_HEADER_MEMBERS = 16

PAD_SECTION_X = 32
PAD_SECTION_Y = 16
PAD_DASHED_INSET = 10
GAP_PREVIEW_TO_BUTTON = 16
GAP_PRODUCT_CARDS = 12

DATASET_DIR = PROJECT_ROOT / "data" / "dataset"
FILES_DIR = PROJECT_ROOT / "data" / "files"
EMBEDDINGS_PATH = FILES_DIR / "embeddings.pkl"
FILENAMES_PATH = FILES_DIR / "filenames.pkl"
RECOMMENDATION_COUNT = 5
NEIGHBOR_SEARCH_K = 20

IMAGE_FILE_TYPES = [
    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
    ("All files", "*.*"),
]
