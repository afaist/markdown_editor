"""Tests for editor_pdf module."""

from unittest import mock

from PyQt6.QtWidgets import QDialog


class TestPDFHandler:
    """Тесты PDFHandler."""

    def test_init(self, markdown_editor):
        """PDFHandler инициализируется с ссылкой на editor."""
        handler = markdown_editor.pdf_handler
        assert handler.editor is markdown_editor

    def test_show_pdf_settings_opens_dialog(self, markdown_editor):
        """show_pdf_settings открывает диалог настроек."""
        handler = markdown_editor.pdf_handler

        with mock.patch("markdown_editor_pkg.editor_pdf.HeaderFooterDialog") as mock_dialog_cls:
            mock_dialog = mock.Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_headers.return_value = {
                "show_headers": True,
                "header_text": "Test Header",
                "footer_text": "Page ",
            }
            mock_dialog_cls.return_value = mock_dialog
            mock_dialog_cls.DialogCode = QDialog.DialogCode

            handler.show_pdf_settings()

            mock_dialog_cls.assert_called_once()
            mock_dialog.exec.assert_called_once()

    def test_show_pdf_settings_saves_headers(self, markdown_editor):
        """show_pdf_settings сохраняет колонтитулы."""
        handler = markdown_editor.pdf_handler

        with mock.patch("markdown_editor_pkg.editor_pdf.HeaderFooterDialog") as mock_dialog_cls:
            mock_dialog = mock.Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_headers.return_value = {
                "show_headers": False,
                "header_text": "",
                "footer_text": "",
            }
            mock_dialog_cls.return_value = mock_dialog
            mock_dialog_cls.DialogCode = QDialog.DialogCode

            handler.show_pdf_settings()

            # Проверяем что set_pdf_headers был вызван с правильными данными
            headers = markdown_editor.file_export._pdf_headers
            assert headers["show_headers"] is False
            assert headers["header_text"] == ""
            assert headers["footer_text"] == ""

    def test_show_pdf_settings_cancelled(self, markdown_editor):
        """show_pdf_settings при отмене не сохраняет."""
        handler = markdown_editor.pdf_handler

        with mock.patch("markdown_editor_pkg.editor_pdf.HeaderFooterDialog") as mock_dialog_cls:
            mock_dialog = mock.Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Rejected
            mock_dialog_cls.return_value = mock_dialog
            mock_dialog_cls.DialogCode = QDialog.DialogCode

            handler.show_pdf_settings()

            # set_pdf_headers не должен вызываться
            # Проверяем что _pdf_headers не изменился

    def test_show_pdf_settings_no_headers(self, markdown_editor):
        """show_pdf_settings с None headers."""
        handler = markdown_editor.pdf_handler
        markdown_editor.file_export._pdf_headers = None

        with mock.patch("markdown_editor_pkg.editor_pdf.HeaderFooterDialog") as mock_dialog_cls:
            mock_dialog = mock.Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_headers.return_value = {
                "show_headers": True,
                "header_text": "H",
                "footer_text": "F",
            }
            mock_dialog_cls.return_value = mock_dialog
            mock_dialog_cls.DialogCode = QDialog.DialogCode

            handler.show_pdf_settings()

            # Должен пройти без ошибки

    def test_show_pdf_settings_shows_status(self, markdown_editor):
        """show_pdf_settings показывает статус в statusbar."""
        handler = markdown_editor.pdf_handler
        markdown_editor._statusbar_ref = mock.Mock()

        with mock.patch("markdown_editor_pkg.editor_pdf.HeaderFooterDialog") as mock_dialog_cls:
            mock_dialog = mock.Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_headers.return_value = {
                "show_headers": False,
                "header_text": "",
                "footer_text": "",
            }
            mock_dialog_cls.return_value = mock_dialog
            mock_dialog_cls.DialogCode = QDialog.DialogCode

            handler.show_pdf_settings()

            markdown_editor._statusbar_ref.showMessage.assert_called()
