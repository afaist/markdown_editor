"""Help Handler — About dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QMessageBox

from markdown_editor_pkg.i18n import tr

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class HelpHandler:
    """Help handler and About dialog."""

    def __init__(self, editor: MarkdownEditorPyQt):
        self.editor = editor

    def show_about(self) -> None:
        """Show the About dialog."""
        QMessageBox.about(
            self.editor,
            tr("About"),
            tr("Markdown Editor (PyQt6)\n\n"
               "Version: 1.0\n"
               "Developed with Python 3.12+, PyQt6, QtWebEngine\n"
               "LaTeX and Markdown support."),
        )
