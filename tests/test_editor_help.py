"""Tests for editor_help module."""

from unittest import mock

from PyQt6.QtWidgets import QDialog

from markdown_editor_pkg.editor_help import HelpHandler


class TestHelpHandler:
    """Тесты HelpHandler."""

    def test_init(self, markdown_editor):
        """HelpHandler инициализируется с ссылкой на editor."""
        handler = markdown_editor.help_handler
        assert handler.editor is markdown_editor

    def test_show_about_creates_dialog(self, markdown_editor):
        """show_about создаёт QDialog."""
        handler = markdown_editor.help_handler

        # Проверяем что метод выполняется без ошибок
        # QDialog создаётся внутри метода
        with mock.patch.object(QDialog, "exec", return_value=0):
            handler.show_about()

    def test_show_shortcuts_creates_dialog(self, markdown_editor):
        """show_shortcuts создаёт QDialog."""
        handler = markdown_editor.help_handler

        with mock.patch.object(QDialog, "exec", return_value=0):
            handler.show_shortcuts()

    def test_show_markdown_help_creates_dialog(self, markdown_editor):
        """show_markdown_help создаёт QDialog."""
        handler = markdown_editor.help_handler

        with mock.patch.object(QDialog, "exec", return_value=0):
            handler.show_markdown_help()
