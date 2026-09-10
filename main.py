#!/usr/bin/env python3
"""
Markdown Editor - A simple Markdown editor with preview and LaTeX support.
"""

import json
import os
import sys
from pathlib import Path

# ── GPU acceleration (must be set before any Qt import) ──────────────────

_CONFIG_PATH = Path.home() / ".markdown_editor_config.json"
_disable_gpu = False

if _CONFIG_PATH.exists():
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            _cfg = json.load(f)
        _disable_gpu = bool(_cfg.get("disable_gpu", False))
    except (json.JSONDecodeError, OSError):
        pass

if _disable_gpu:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu --disable-gpu-compositing --disable-software-rasterizer"
        " --disable-gpu-info-update"
    )
    os.environ["QTWEBENGINE_SETTINGS"] = '{"enable_gpu": "false"}'

os.environ["QT_LOGGING_RULES"] = "qt.webengine.services=false"

from PyQt6.QtWidgets import QApplication

from markdown_editor_pkg import __version__
from markdown_editor_pkg.editor import MarkdownEditorPyQt
from markdown_editor_pkg.i18n import setup_translator


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Editor")
    app.setApplicationVersion(__version__)
    setup_translator(app)
    window = MarkdownEditorPyQt()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
