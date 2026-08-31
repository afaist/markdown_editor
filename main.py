#!/usr/bin/env python3
"""
Markdown Editor - Простой редактор Markdown с предпросмотром и поддержкой LaTeX-формул
"""

import os
import sys

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu --disable-gpu-compositing --disable-software-rasterizer"
)

from PyQt6.QtWidgets import QApplication

from markdown_editor_pkg.editor import MarkdownEditorPyQt


def main():
    """Основная функция приложения"""
    app = QApplication(sys.argv)
    window = MarkdownEditorPyQt()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
