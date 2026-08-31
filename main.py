#!/usr/bin/env python3
"""
Markdown Editor - Простой редактор Markdown с предпросмотром и поддержкой LaTeX-формул
"""

import os
import sys

from PyQt6.QtWidgets import QApplication

from markdown_editor_pkg.editor import MarkdownEditorPyQt

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu --disable-gpu-compositing --disable-software-rasterizer"
)


def main():
    """Основная функция приложения"""
    app = QApplication(sys.argv)
    window = MarkdownEditorPyQt()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
