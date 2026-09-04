"""Help Handler — справка «О программе»."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class HelpHandler:
    """Обработчик справки и диалога «О программе»."""

    def __init__(self, editor: MarkdownEditorPyQt):
        self.editor = editor

    def show_about(self) -> None:
        """Показать диалог «О программа»."""
        QMessageBox.about(
            self.editor,
            "О программе",
            "Markdown Editor (PyQt6)\n\n"
            "Версия: 1.0\n"
            "Разработано с использованием Python 3.8+, PyQt6, QtWebEngine\n"
            "Поддержка LaTeX и Markdown.",
        )
