"""Find/Replace handler — диалог поиска и замены."""

from __future__ import annotations

from typing import TYPE_CHECKING

from markdown_editor_pkg.find_replace import FindReplaceDialog

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class FindReplaceHandler:
    """Обработчик диалога поиска и замены."""

    def __init__(self, editor: MarkdownEditorPyQt):
        """Инициализация обработчика поиска и замены.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
        """
        self.editor = editor

    def find_replace(self) -> None:
        """Открыть модальный диалог FindReplaceDialog для поиска и замены текста."""
        dialog = FindReplaceDialog(self.editor)
        dialog.exec_dialog()
