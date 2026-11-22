"""
Markdown Editor - A simple Markdown editor with preview and LaTeX support.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Logging setup (must be before Qt imports) ──────────────────────────

LOG_DIR = Path.home() / ".local" / "share" / "markdown_editor"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"markdown_editor_{datetime.now():%Y%m%d_%H%M%S}.log"

# Root logger — все модули используют logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)
logger.info("=== Markdown Editor starting ===")
logger.info("Log file: %s", LOG_FILE)

# ── GPU acceleration (must be set before any Qt import) ──────────────────

_config_path = Path.home() / ".markdown_editor_config.json"
_disable_gpu = False

if _config_path.exists():
    try:
        with open(_config_path, encoding="utf-8") as f:
            _cfg = json.load(f)
        _disable_gpu = bool(_cfg.get("disable_gpu", False))
    except (json.JSONDecodeError, OSError):
        pass

_chromium_flags = "--log-level=3 --no-sandbox --disable-gpu-info-update"

if _disable_gpu:
    _chromium_flags += " --disable-gpu --disable-gpu-compositing --disable-software-rasterizer"
    os.environ["QTWEBENGINE_SETTINGS"] = '{"enable_gpu": "false"}'

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = _chromium_flags
os.environ["QT_LOGGING_RULES"] = "qt.webengine.services=false"

# ── Force xcb platform to avoid GNOME xsettings schema errors ─────────────
# GTK integration may fail with missing schema keys in newer GNOME versions.
# xcb is more stable and doesn't depend on GTK settings.
# On Windows, let the runtime hook set the platform plugin.
if "QT_QPA_PLATFORM" not in os.environ and os.name == "posix":
    os.environ["QT_QPA_PLATFORM"] = "xcb"

# ── Suppress Chromium/Mesa stderr messages (GBM, GPUInfo, etc.) ──────────
# These messages come from Mesa/Chromium directly to stderr, not via Qt.
# Redirect stderr to /dev/null before QApplication initialization,
# then restore it after the app is created so Python errors are visible.

# ── Disable system GIO modules to avoid glib version conflicts ───────────
# AppImage is built on Ubuntu 24.04 (glib 2.80) and distributed to users
# on older systems (e.g. Ubuntu 22.04 with glib 2.74). The system GIO
# modules (libgvfsdbus.so) are compiled against glib 2.80 and reference
# symbols like g_variant_builder_init_static that do not exist in glib 2.74.
# Qt may try to load these system GIO modules, causing a crash.
#
# We prevent this by:
# 1. QT_QPA_PLATFORMTHEME=none — skip GTK/GIO platform theme integration
# 2. QT_QPA_PLATFORM=xcb — force xcb platform (no GTK integration)
# 3. GIO_EXTRA_MODULES="" — prevent GIO from loading system GIO modules
#
# The AppImage bundles its own Qt6 libraries and plugins, so this is safe.
os.environ["QT_QPA_PLATFORMTHEME"] = "none"
os.environ["GIO_EXTRA_MODULES"] = ""

# ── Force stderr suppression on POSIX systems ──────────────────────────

_stderr_backup = None

if os.name == "posix":
    _devnull_fd = os.open(os.devnull, os.O_WRONLY)
    _stderr_backup = os.dup(2)
    os.dup2(_devnull_fd, 2)
    os.close(_devnull_fd)

from PyQt6.QtWidgets import QApplication, QMessageBox

from markdown_editor_pkg import __version__
from markdown_editor_pkg.editor import MarkdownEditorPyQt
from markdown_editor_pkg.i18n import setup_translator

# ── Global exception handler ─────────────────────────────────────────────


def _uncaught_exception_handler(exc_type, exc_value, exc_traceback) -> None:
    """Catch all unhandled exceptions and show user-friendly dialog."""
    if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    # Show dialog
    import sys

    if hasattr(sys, "ps1"):
        # Interactive mode — don't show dialog
        return
    QMessageBox.critical(
        None,
        "Critical Error",
        f"An unexpected error occurred.\n\n"
        f"Details: {exc_type.__name__}: {exc_value}\n\n"
        f"Log file: {LOG_FILE}\n\n"
        f"Please report this issue with the log file.",
    )


sys.excepthook = _uncaught_exception_handler


def main() -> None:
    """Main application entry point."""
    # Restore stderr after Qt initialization so Python errors are visible
    global _stderr_backup
    if _stderr_backup is not None:
        os.dup2(_stderr_backup, 2)
        os.close(_stderr_backup)
        _stderr_backup = None

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Markdown Editor")
        app.setApplicationVersion(__version__)
        setup_translator(app)
        window = MarkdownEditorPyQt()
        window.show()
        logger.info("Application started successfully")
        sys.exit(app.exec())
    except Exception:
        logger.critical("Fatal error during startup", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
