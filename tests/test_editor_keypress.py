"""Tests for editor_keypress module — auto-continuation of lists and quotes."""

from unittest import mock

import pytest
from PyQt6.QtCore import Qt

from markdown_editor_pkg.editor_keypress import (
    MarkdownTextEdit,
    _get_blockquote_prefix,
    _get_heading_info,
    _get_list_marker,
    _is_empty_blockquote,
    _is_empty_list_item,
)


class TestGetListMarker:
    """Тесты _get_list_marker()."""

    def test_unordered_dash(self):
        """Неупорядоченный список с дефисом."""
        result = _get_list_marker("- item")
        assert result == ("", "- ")

    def test_unordered_star(self):
        """Неупорядоченный список со звёздочкой."""
        result = _get_list_marker("* item")
        assert result == ("", "* ")

    def test_unordered_plus(self):
        """Неупорядоченный список с плюсом."""
        result = _get_list_marker("+ item")
        assert result == ("", "+ ")

    def test_ordered_list(self):
        """Упорядоченный список."""
        result = _get_list_marker("1. item")
        assert result == ("", "1. ")

    def test_ordered_list_different_number(self):
        """Упорядоченный список с другим номером."""
        result = _get_list_marker("5. item")
        assert result == ("", "5. ")

    def test_indented_list(self):
        """Вложенный список с отступом."""
        result = _get_list_marker("    - item")
        assert result == ("    ", "- ")

    def test_not_a_list(self):
        """Обычный текст не является списком."""
        result = _get_list_marker("Just text")
        assert result is None

    def test_empty_line(self):
        """Пустая строка."""
        result = _get_list_marker("")
        assert result is None


class TestIsEmptyListItem:
    """Тесты _is_empty_list_item()."""

    def test_empty_unordered_dash(self):
        """Пустой элемент неупорядоченного списка (дефис)."""
        result = _is_empty_list_item("- ")
        assert result is not None
        assert result[0] is True

    def test_empty_unordered_star(self):
        """Пустой элемент неупорядоченного списка (звёздочка)."""
        result = _is_empty_list_item("* ")
        assert result is not None

    def test_empty_ordered(self):
        """Пустой элемент упорядоченного списка."""
        result = _is_empty_list_item("1. ")
        assert result is not None

    def test_non_empty_list_item(self):
        """Непустой элемент списка."""
        result = _is_empty_list_item("- item")
        assert result is None

    def test_just_marker_no_space(self):
        """Только маркер без пробела — всё ещё считается пустым (\\s* совпадает с 0 символами)."""
        result = _is_empty_list_item("-")
        # Regex \s* совпадает с нулём символов, поэтому "-" считается пустым элементом
        assert result is not None


class TestIsEmptyBlockquote:
    """Тесты _is_empty_blockquote()."""

    def test_empty_blockquote(self):
        """Пустая цитата."""
        result = _is_empty_blockquote("> ")
        assert result is not None
        assert result[0] is True

    def test_non_empty_blockquote(self):
        """Непустая цитата."""
        result = _is_empty_blockquote("> text")
        assert result is None

    def test_not_a_blockquote(self):
        """Не цитата."""
        result = _is_empty_blockquote("Just text")
        assert result is None


class TestGetBlockquotePrefix:
    """Тесты _get_blockquote_prefix()."""

    def test_blockquote_prefix(self):
        """Префикс цитаты."""
        result = _get_blockquote_prefix("> text")
        assert result == ("", "> ")

    def test_indented_blockquote(self):
        """Вложенная цитата."""
        result = _get_blockquote_prefix("    > text")
        assert result == ("    ", "> ")

    def test_not_a_blockquote(self):
        """Не цитата."""
        result = _get_blockquote_prefix("Just text")
        assert result is None


class TestGetHeadingInfo:
    """Тесты _get_heading_info()."""

    def test_heading_h1(self):
        """Заголовок H1."""
        assert _get_heading_info("# Title") is True

    def test_heading_h2(self):
        """Заголовок H2."""
        assert _get_heading_info("## Title") is True

    def test_heading_h6(self):
        """Заголовок H6."""
        assert _get_heading_info("###### Title") is True

    def test_not_a_heading(self):
        """Не заголовок."""
        assert _get_heading_info("Just text") is False

    def test_heading_too_deep(self):
        """Заголовок глубже H6 не считается."""
        assert _get_heading_info("####### Title") is False

    def test_heading_no_space(self):
        """Заголовок без пробела."""
        assert _get_heading_info("#Title") is False


class TestMarkdownTextEdit:
    """Тесты MarkdownTextEdit."""

    @pytest.fixture
    def text_edit(self):
        """Создаёт MarkdownTextEdit для тестов."""
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            import sys

            from PyQt6.QtWidgets import QApplication as _QApp

            app = _QApp(sys.argv)

        widget = MarkdownTextEdit()
        yield widget
        widget.deleteLater()

    def test_insert_unordered_list(self, text_edit):
        """Вставка неупорядоченного списка."""
        text_edit.setPlainText("- item")
        cursor = text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)

        # Симулируем нажатие Enter
        event = self._make_key_event(Qt.Key.Key_Return)
        text_edit.keyPressEvent(event)

        # После первого элемента — новая строка с маркером
        assert "\n- " in text_edit.toPlainText()

    def test_insert_ordered_list(self, text_edit):
        """Вставка упорядоченного списка."""
        text_edit.setPlainText("1. item")
        cursor = text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)

        event = self._make_key_event(Qt.Key.Key_Return)
        text_edit.keyPressEvent(event)

        assert "\n1. " in text_edit.toPlainText()

    def test_insert_blockquote(self, text_edit):
        """Вставка цитаты."""
        text_edit.setPlainText("> quote")
        cursor = text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)

        event = self._make_key_event(Qt.Key.Key_Return)
        text_edit.keyPressEvent(event)

        assert "\n> " in text_edit.toPlainText()

    def test_insert_heading(self, text_edit):
        """Вставка заголовка создаёт дополнительную пустую строку."""
        text_edit.setPlainText("# Title")
        cursor = text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)

        event = self._make_key_event(Qt.Key.Key_Return)
        text_edit.keyPressEvent(event)

        # Заголовок + пустая строка (заголовок без списка/цитаты не вставляет префикс)
        text = text_edit.toPlainText()
        assert text == "# Title\n\n"

    def test_regular_text_no_auto_continue(self, text_edit):
        """Обычный текст не получает авто-продолжения."""
        text_edit.setPlainText("Just text")
        cursor = text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)

        event = self._make_key_event(Qt.Key.Key_Return)
        text_edit.keyPressEvent(event)

        text = text_edit.toPlainText()
        # После Enter просто новая строка без маркеров
        assert text == "Just text\n"

    def _make_key_event(self, key):
        """Создаёт mock QKeyEvent."""
        event = mock.Mock()
        event.key.return_value = key
        return event
