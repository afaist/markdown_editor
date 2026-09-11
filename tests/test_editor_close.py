"""Tests for editor_close module."""

from unittest import mock

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox


class TestCloseHandler:
    """Тесты CloseHandler."""

    def test_init(self, markdown_editor):
        """CloseHandler инициализируется с ссылкой на editor."""
        handler = markdown_editor.close_handler
        assert handler.editor is markdown_editor

    def test_on_close_no_changes_accepts(self, markdown_editor):
        """on_close без изменений принимает закрытие."""
        handler = markdown_editor.close_handler
        markdown_editor.is_dirty = False

        event = mock.Mock(spec=QCloseEvent)
        handler.on_close(event)

        event.accept.assert_called_once()

    def test_on_close_dirty_cancel_ignores(self, markdown_editor):
        """on_close: Cancel — игнорирует закрытие."""
        handler = markdown_editor.close_handler
        markdown_editor.is_dirty = True

        event = mock.Mock(spec=QCloseEvent)

        mock_msgbox = mock.Mock()
        mock_msgbox.exec.return_value = QMessageBox.StandardButton.Cancel

        with mock.patch(
            "markdown_editor_pkg.editor_close.QMessageBox", return_value=mock_msgbox
        ) as mock_cls:
            mock_cls.StandardButton = QMessageBox.StandardButton
            handler.on_close(event)

        event.ignore.assert_called_once()

    def test_on_close_dirty_discard_accepts(self, markdown_editor):
        """on_close: Discard — принимает закрытие."""
        handler = markdown_editor.close_handler
        markdown_editor.is_dirty = True

        event = mock.Mock(spec=QCloseEvent)

        mock_msgbox = mock.Mock()
        mock_msgbox.exec.return_value = QMessageBox.StandardButton.Discard

        with mock.patch(
            "markdown_editor_pkg.editor_close.QMessageBox", return_value=mock_msgbox
        ) as mock_cls:
            mock_cls.StandardButton = QMessageBox.StandardButton
            handler.on_close(event)

        event.accept.assert_called_once()

    def test_on_close_none_event(self, markdown_editor):
        """on_close с None event не падает."""
        handler = markdown_editor.close_handler
        handler.on_close(None)
        # Должен вернуться без ошибки
