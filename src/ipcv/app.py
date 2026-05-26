"""
Application entry point for the Visual Recommender System desktop client.

Starts console logging, builds the main CustomTkinter window, and runs the
event loop until the user closes the application.
"""

from ipcv.logging_config import get_logger, setup_logging
from ipcv.ui.main_window import MainWindow

logger = get_logger("app")


def run() -> None:
    """
    Initialize logging, create the main window, and enter the GUI main loop.

    Blocks until the user closes the window. Recommendation index preload
    begins automatically inside ``MainWindow``.
    """
    setup_logging()
    logger.info("Starting Visual Recommender System")
    app = MainWindow()
    logger.info("Main window ready — waiting for user input")
    app.mainloop()
    logger.info("Application closed")


if __name__ == "__main__":
    run()
