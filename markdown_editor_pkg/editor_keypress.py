"""Автопродолжение списков и цитат при нажатии Enter."""

from __future__ import annotations

import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QTextEdit

# Паттерны для определения типа текущей строки
_UNORDERED_LIST_RE = re.compile(r"^(\s*)([-*+])\s")
_ORDERED_LIST_RE = re.compile(r"^(\s*)(\d+)\.\s")
_BLOCKQUOTE_RE = re.compile(r"^(\s*)(>\s*)")
_HEADING_RE = re.compile(r"^#{1,6}\s+.+")

# Паттерны для проверки, что строка содержит ТОЛЬКО маркер (без текста)
_UNORDERED_EMPTY_RE = re.compile(r"^(\s*)([-*+])\s*$")
_ORDERED_EMPTY_RE = re.compile(r"^(\s*)(\d+)\.\s*$")


def _get_list_marker(line: str) -> tuple[str, str] | None:
    """Возвращает (indent, marker) для списка или None."""
    m = _UNORDERED_LIST_RE.match(line)
    if m:
        return m.group(1), f"{m.group(2)} "
    m = _ORDERED_LIST_RE.match(line)
    if m:
        return m.group(1), f"{m.group(2)}. "
    return None


def _is_empty_list_item(line: str) -> tuple[bool, str, str] | None:
    """Проверяет, содержит ли строка только маркер списка без текста.

    Возвращает (True, indent, marker) если строка — пустой элемент списка,
    None если это не пустой элемент списка.
    """
    m = _UNORDERED_EMPTY_RE.match(line)
    if m:
        return True, m.group(1), f"{m.group(2)} "
    m = _ORDERED_EMPTY_RE.match(line)
    if m:
        return True, m.group(1), f"{m.group(2)}. "
    return None


def _is_empty_blockquote(line: str) -> tuple[bool, str] | None:
    """Проверяет, содержит ли строка только маркер цитаты без текста.

    Возвращает (True, prefix) если строка — пустая цитата,
    None если это не пустая цитата.
    """
    m = _BLOCKQUOTE_RE.match(line)
    if m:
        prefix = m.group(2)  # это "> "
        # Проверяем, что после префикса нет значимого текста
        remaining = line[m.end():]
        if remaining.strip() == "":
            return True, prefix
    return None


def _get_blockquote_prefix(line: str) -> tuple[str, str] | None:
    """Возвращает (indent, prefix) для цитаты или None."""
    m = _BLOCKQUOTE_RE.match(line)
    if m:
        return m.group(1), f"{m.group(2)}"
    return None


def _get_heading_info(line: str) -> bool:
    """Возвращает True, если строка является заголовком Markdown."""
    return _HEADING_RE.match(line) is not None


class MarkdownTextEdit(QTextEdit):
    """QTextEdit с автопродолжением списков и цитат."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        if (
            e is not None
            and e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and self._try_auto_continue()
        ):
            return  # Обработали — не вызываем суперкласс

        super().keyPressEvent(e)

    def _try_auto_continue(self) -> bool:
        """Пытаемся продолжить список/цитату. Возвращает True если продолжили."""
        cursor = self.textCursor()
        block = cursor.block()
        text = block.text()

        # Проверяем, является ли строка пустым элементом списка
        empty_list = _is_empty_list_item(text)

        if empty_list is not None:
            # Пустой элемент списка — завершаем список
            # Удаляем маркер с текущей строки (оставляем строку пустой)
            # Удаляем: от начала строки до конца маркера
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            # Вставляем пустую строку и не добавляем маркер
            cursor.insertText("\n")
            return True

        # Проверяем, является ли строка пустой цитатой
        empty_bq = _is_empty_blockquote(text)

        if empty_bq is not None:
            # Пустая цитата — завершаем цитату
            # Удаляем маркер цитаты с текущей строки
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText("\n")
            return True

        # Определяем тип текущей строки
        list_info = _get_list_marker(text)
        bq_info = _get_blockquote_prefix(text)
        heading_info = _get_heading_info(text)

        if list_info is None and bq_info is None and heading_info is None:
            return False

        # Вычисляем префикс для новой строки
        prefix_parts: list[str] = []

        if list_info:
            indent, marker = list_info
            if bq_info:
                # Цитата + список: > - элемент
                prefix_parts.append(f"{bq_info[1]}{marker}")
            else:
                prefix_parts.append(f"{indent}{marker}")
        elif bq_info:
            # Только цитата
            prefix_parts.append(f"{bq_info[1]}")

        prefix = "".join(prefix_parts)

        # Разрываем текущую строку — это создаст новую строку и переместит курсор
        cursor.insertText("\n")
        # Вставляем префикс в начало новой строки
        cursor.insertText(prefix)

        # Для заголовка — ещё одна пустая строка
        if heading_info:
            cursor.insertText("\n")

        return True
