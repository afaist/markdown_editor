"""Find/Replace handler — диалог поиска и замены."""

from markdown_editor_pkg.find_replace import FindReplaceDialog


class FindReplaceHandler:
    """Обработчик диалога поиска и замены."""

    def __init__(self, editor: "MarkdownEditorPyQt"):
        self.editor = editor

    def find_replace(self) -> None:
        """Открыть диалог поиска и замены."""
        dialog = FindReplaceDialog(self.editor)
        dialog.exec_dialog()
