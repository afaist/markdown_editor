#!/usr/bin/env python3
"""
Markdown Editor - Простой редактор Markdown с предпросмотром и поддержкой LaTeX-формул
"""

from markdown_editor_pkg.editor import MarkdownEditorPyQt
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def main():
    """Основная функция приложения"""
    app = QApplication(sys.argv)
    window = MarkdownEditorPyQt()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
