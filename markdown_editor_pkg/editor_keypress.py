"""Область отображения номеров строк слева от текста + автопродолжение списков.

Содержит:
- LineNumberArea — панель с номерами строк
- MarkdownTextEdit — QTextEdit с номерами строк и автопродолжением списков
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from PyQt6.QtCore import QMargins, QRect, QSize, Qt
from PyQt6.QtGui import QKeyEvent, QPainter
from PyQt6.QtWidgets import QTextEdit

if TYPE_CHECKING:
    from PyQt6.QtGui import QTextBlock

# ─── Паттерны для автопродолжения ────────────────────────────────────────────

_UNORDERED_LIST_RE = re.compile(r"^(\s*)([-*+])\s")
_ORDERED_LIST_RE = re.compile(r"^(\s*)(\d+)\.\s")
_BLOCKQUOTE_RE = re.compile(r"^(\s*)(>\s*)")
_HEADING_RE = re.compile(r"^#{1,6}\s+.+")

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
    """Проверяет, содержит ли строка только маркер списка без текста."""
    m = _UNORDERED_EMPTY_RE.match(line)
    if m:
        return True, m.group(1), f"{m.group(2)} "
    m = _ORDERED_EMPTY_RE.match(line)
    if m:
        return True, m.group(1), f"{m.group(2)}. "
    return None


def _is_empty_blockquote(line: str) -> tuple[bool, str] | None:
    """Проверяет, содержит ли строка только маркер цитаты без текста."""
    m = _BLOCKQUOTE_RE.match(line)
    if m:
        prefix = m.group(2)
        remaining = line[m.end() :]
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


class LineNumberArea(QTextEdit):
    """Панель с номерами строк, отображаемая слева от текста."""

    def __init__(self, editor: QTextEdit, parent: QTextEdit | None = None) -> None:
        """Инициализация области номеров строк.

        Args:
            editor: QTextEdit, к которому привязана область номеров строк.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._editor = editor
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color: #f5f5f5; "
            "color: #888888; "
            "font-family: Consolas, 'Courier New', monospace; "
            "font-size: 11px;"
        )

    def sizeHint(self) -> QSize:  # type: ignore[name-defined]
        """Возвращает рекомендуемый размер области номеров строк."""
        return QRect(0, 0, self._editor.line_number_area_width(), 0).size()  # type: ignore[attr-defined]

    def paintEvent(self, event) -> None:  # type: ignore[override]
        """Перерисовывает номера строк."""
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.GlobalColor.white)

        # mypy: QTextEdit.firstVisibleBlock() not in stubs
        block: QTextBlock = self._editor.firstVisibleBlock()  # type: ignore[attr-defined]
        line_number = block.blockNumber() + 1
        height = self._editor.fontMetrics().height()

        while block.isValid():
            # mypy: isHidden() is Qt-specific, not in stubs
            if block.isVisible() and not block.isHidden():  # type: ignore[attr-defined]
                # Выравнивание по правому краю
                text = str(line_number)
                painter.setPen(Qt.GlobalColor.darkGray)
                # mypy: verticalScrollBar() can be None
                sb = self._editor.verticalScrollBar()
                sb_value = sb.value() if sb is not None else 0
                # mypy: textCursor().block() can be None
                cursor_block = self._editor.textCursor().block()
                painter.drawText(
                    4,
                    int(
                        self.y()
                        + self._editor.fontMetrics().height() * line_number
                        - sb_value
                        - cursor_block.position()
                    ),
                    self.width() - 8,
                    height,
                    Qt.AlignmentFlag.AlignRight,
                    text,
                )
            else:
                # Пропускаем скрытые блоки
                pass

            block = block.next()
            line_number += 1

        painter.end()


class MarkdownTextEdit(QTextEdit):
    """QTextEdit с автопродолжением списков, цитат, заголовков и номерами строк.

    При нажатии Enter на пустом элементе списка или цитаты завершает
    список/цитату. На строке с маркером — продолжает с тем же маркером.
    """

    def __init__(self, parent=None) -> None:
        """Инициализация кастомного QTextEdit.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._line_number_area: LineNumberArea | None = None
        self._show_line_numbers = False
        self._connect_line_number_signals()

    def _connect_line_number_signals(self) -> None:
        """Подключает сигналы для обновления области номеров строк."""
        try:
            # mypy: Qt signals not in stubs
            self.blockCountChanged.connect(self._update_line_number_area_width)  # type: ignore[attr-defined]
        except AttributeError:
            pass
        try:
            self.updateRequest.connect(self._update_line_number_area)  # type: ignore[attr-defined]
        except AttributeError:
            pass

    def line_number_area_width(self) -> int:
        """Возвращает ширину области номеров строк."""
        if not self._show_line_numbers:
            return 0
        doc = self.document()
        if doc is None:
            return 0
        digits = max(1, len(str(doc.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance(str(digits)) + 10
        return space

    def _update_line_number_area_width(self) -> None:
        """Обновляет ширину области номеров строк."""
        adjustment = self.line_number_area_width()
        vp = self.viewport()
        if vp is not None and adjustment != vp.width():
            self.setViewportMargins(QMargins(adjustment, 0, 0, 0))  # type: ignore[attr-defined]

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:  # type: ignore[reportUnknownVariableType]
        """Перерисовывает область номеров строк при изменении содержимого."""
        if self._line_number_area is None:
            return
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, int(rect.top()), self._line_number_area.width(), int(rect.height())
            )

        vp = self.viewport()
        if vp is not None and rect.contains(vp.rect()):
            self._update_line_number_area_width()

    def set_show_line_numbers(self, show: bool) -> None:
        """Включает/выключает отображение номеров строк.

        Args:
            show: True для отображения номеров строк.
        """
        if self._show_line_numbers == show:
            return

        self._show_line_numbers = show

        if show:
            if self._line_number_area is None:
                self._line_number_area = LineNumberArea(self, self)
            self._update_line_number_area_width()
        else:
            if self._line_number_area is not None:
                self._line_number_area.deleteLater()
                self._line_number_area = None
            self._update_line_number_area_width()

    def is_show_line_numbers(self) -> bool:
        """Возвращает True если номера строк включены."""
        return self._show_line_numbers

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        """Обработка изменения размера редактора."""
        super().resizeEvent(event)
        if self._line_number_area is not None:
            cr = self.contentsRect()
            self._line_number_area.setGeometry(
                QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
            )

    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        """Обработка нажатия клавиш с автопродолжением списков и цитат.

        Args:
            e: Объект события клавиатуры.
        """
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
