"""PDF Handler — логика PDF-экспорта и настроек."""

from __future__ import annotations

from typing import TYPE_CHECKING

from markdown_editor_pkg.header_footer_dialog import HeaderFooterDialog

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class PDFHandler:
    """Обработчик PDF-настроек и экспорта."""

    def __init__(self, editor: MarkdownEditorPyQt):
        """Инициализация обработчика PDF-экспорта.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
        """
        self.editor = editor

    def show_pdf_settings(self) -> None:
        """Открыть диалог настроек PDF-экспорта."""
        current_headers = (
            self.editor.file_export._pdf_headers
            if self.editor.file_export._pdf_headers is not None
            else {}
        )
        dialog = HeaderFooterDialog(self.editor, current_headers=current_headers)
        if dialog.exec() == HeaderFooterDialog.DialogCode.Accepted:
            headers = dialog.get_headers()
            self.editor.file_export.set_pdf_headers(headers)
            if self.editor._statusbar_ref:
                status = (
                    "Настройки PDF-экспорта сохранены"
                    if headers["show_headers"]
                    else "Колонтитулы PDF отключены"
                )
                self.editor._statusbar_ref.showMessage(status)
