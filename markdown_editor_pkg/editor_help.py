"""Help Handler — справка «О программе»."""

from PyQt6.QtWidgets import QMessageBox


class HelpHandler:
    """Обработчик справки и диалога «О программе»."""

    def __init__(self, editor: "MarkdownEditorPyQt"):
        self.editor = editor

    def show_about(self) -> None:
        """Показать диалог «О программе»."""
        QMessageBox.about(
            self.editor,
            "О программе",
            "Markdown Editor (PyQt6)\n\n"
            "Версия: 1.0\n"
            "Разработано с использованием Python 3.8+, PyQt6, QtWebEngine\n"
            "Поддержка LaTeX и Markdown.",
        )
