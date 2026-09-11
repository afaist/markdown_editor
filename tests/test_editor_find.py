"""Tests for editor_find module."""

from unittest import mock


class TestFindReplaceHandler:
    """Тесты FindReplaceHandler."""

    def test_init(self, markdown_editor):
        """FindReplaceHandler инициализируется с ссылкой на editor."""
        handler = markdown_editor.find_replace_handler
        assert handler.editor is markdown_editor

    def test_find_replace_opens_dialog(self, markdown_editor):
        """find_replace открывает диалог поиска."""
        handler = markdown_editor.find_replace_handler

        with mock.patch("markdown_editor_pkg.editor_find.FindReplaceDialog") as mock_dialog_cls:
            mock_dialog = mock.Mock()
            mock_dialog_cls.return_value = mock_dialog

            handler.find_replace()

            mock_dialog_cls.assert_called_once_with(markdown_editor)
            mock_dialog.exec_dialog.assert_called_once()

    def test_find_replace_creates_dialog_with_editor(self, markdown_editor):
        """find_replace создаёт диалог с правильным editor."""
        handler = markdown_editor.find_replace_handler

        with mock.patch("markdown_editor_pkg.editor_find.FindReplaceDialog") as mock_dialog_cls:
            mock_dialog = mock.Mock()
            mock_dialog_cls.return_value = mock_dialog

            handler.find_replace()

            args, _kwargs = mock_dialog_cls.call_args
            assert args[0] is markdown_editor
