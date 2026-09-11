"""Tests for editor_session module."""

import os
from unittest import mock

from markdown_editor_pkg.editor_session import SessionHandler


class TestSessionHandler:
    """Тесты SessionHandler."""

    def test_init(self, markdown_editor):
        """SessionHandler инициализируется с ссылкой на editor."""
        handler = markdown_editor.session_handler
        assert handler.editor is markdown_editor

    def test_save_session_calls_manager(self, markdown_editor):
        """save_session вызывает SessionManager.save()."""
        handler = markdown_editor.session_handler

        with mock.patch(
            "markdown_editor_pkg.editor_session.SessionManager.save"
        ) as mock_save:
            handler.save_session("/path/to/file.md")
            mock_save.assert_called_once_with("/path/to/file.md")

    def test_load_session_file_not_exists(self, markdown_editor):
        """load_session не делает ничего если файл не существует."""
        handler = markdown_editor.session_handler

        with mock.patch(
            "markdown_editor_pkg.editor_session.SessionManager.load"
        ) as mock_load:
            mock_load.return_value = "/nonexistent/file.md"
            # Не должно вызвать исключение
            handler.load_session()

    def test_load_session_file_exists(self, markdown_editor, tmp_md):
        """load_session загружает существующий файл."""
        # Создаём тестовый файл
        tmp_md.write_text("# Test Content")

        handler = markdown_editor.session_handler

        with mock.patch(
            "markdown_editor_pkg.editor_session.SessionManager.load"
        ) as mock_load, \
             mock.patch("os.path.exists") as mock_exists:
            mock_load.return_value = str(tmp_md)
            mock_exists.return_value = True

            handler.load_session()

            assert markdown_editor.editor.toPlainText() == "# Test Content"
            assert markdown_editor.current_file == str(tmp_md)
            assert markdown_editor.is_dirty is False

    def test_load_session_corrupted_file(self, markdown_editor):
        """load_session корректно обрабатывает нечитаемый файл."""
        handler = markdown_editor.session_handler

        with mock.patch(
            "markdown_editor_pkg.editor_session.SessionManager.load"
        ) as mock_load, \
             mock.patch("os.path.exists") as mock_exists:
            mock_load.return_value = "/path/to/corrupted.md"
            mock_exists.return_value = True

            # Файл существует, но чтение вызывает ошибку
            with mock.patch(
                "builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "test reason")
            ):
                # Должен обработать ошибку без падения
                # logger.exception вызывается внутри
                handler.load_session()
