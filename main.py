#!/usr/bin/env python3
"""
Markdown Editor - A simple Markdown editor with preview and LaTeX support.
"""

import os
import sys

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu --disable-gpu-compositing --disable-software-rasterizer"
)
os.environ["QTWEBENGINE_SETTINGS"] = '{"enable_gpu": "false"}'

from PyQt6.QtWidgets import QApplication

from markdown_editor_pkg.editor import MarkdownEditorPyQt
from markdown_editor_pkg.i18n import setup_translator


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Editor")
    setup_translator(app)
    window = MarkdownEditorPyQt()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
