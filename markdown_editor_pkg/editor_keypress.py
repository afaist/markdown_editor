"""Область отображения номеров строк слева от текста + автопродолжение списков.

Содержит:
- MarkdownTextEdit — QPlainTextEdit с номерами строк и автопродолжением списков
"""

from __future__ import annotations

import re

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QKeyEvent, QPainter
from PyQt6.QtWidgets import QPlainTextEdit, QWidget

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
    """Проверяет, содержит ли строку только маркер цитаты без текста."""
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


class LineNumberArea(QWidget):
    """Панель с номерами строк, отображаемая слева от текста."""

    def __init__(self, editor: QPlainTextEdit) -> None:
        """Инициализация области номеров строк.

        Args:
            editor: QPlainTextEdit, к которому привязана область номеров строк.
        """
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:  # type: ignore[override]
        """Возвращает рекомендуемый размер области номеров строк."""
        # mypy: line_number_area_width is on MarkdownTextEdit, not QPlainTextEdit
        return QSize(self._editor.line_number_area_width(), 0)  # type: ignore[attr-defined]

    def paintEvent(self, event) -> None:  # type: ignore[override]
        """Перерисовывает номера строк."""
        # mypy: line_number_area_paint_event is on MarkdownTextEdit, not QPlainTextEdit
        self._editor.line_number_area_paint_event(event)  # type: ignore[attr-defined]


class MarkdownTextEdit(QPlainTextEdit):
    """QPlainTextEdit с автопродолжением списков, цитат, заголовков и номерами строк.

    При нажатии Enter на пустом элементе списка или цитаты завершает
    список/цитату. На строке с маркером — продолжает с тем же маркером.

    Номера строк реализованы через отдельный виджет LineNumberArea,
    который накладывается слева на область viewport (viewport margin).
    """

    def __init__(self, parent=None) -> None:
        """Инициализация кастомного QPlainTextEdit.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._line_number_area: LineNumberArea | None = None
        self._show_line_numbers = False
        self._connect_line_number_signals()

    def _connect_line_number_signals(self) -> None:
        """Подключает сигналы для обновления области номеров строк."""
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)

    def line_number_area_width(self) -> int:
        """Возвращает ширину области номеров строк."""
        if not self._show_line_numbers:
            return 0
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits + 10
        return space

    def _update_line_number_area_width(self, _=0) -> None:
        """Обновляет ширину области номеров строк."""
        adjustment = self.line_number_area_width()
        if adjustment != self.viewportMargins().left():
            self.setViewportMargins(adjustment, 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        """Перерисовывает область номеров строк при изменении содержимого."""
        if self._line_number_area is None:
            return
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, rect.y(), self._line_number_area.width(), rect.height()
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
                self._line_number_area = LineNumberArea(self)
            self._update_line_number_area_width()
            self._update_line_number_area_geometry()
            self._line_number_area.show()
            self._line_number_area.update()
        else:
            if self._line_number_area is not None:
                self._line_number_area.deleteLater()
                self._line_number_area = None
            self._update_line_number_area_width()

    def _update_line_number_area_geometry(self) -> None:
        """Обновляет геометрию области номеров строк."""
        if self._line_number_area is not None:
            cr = self.contentsRect()
            self._line_number_area.setGeometry(
                QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
            )

    def is_show_line_numbers(self) -> bool:
        """Возвращает True если номера строк включены."""
        return self._show_line_numbers

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        """Обработка изменения размера редактора."""
        super().resizeEvent(event)
        self._update_line_number_area_geometry()

    def line_number_area_paint_event(self, event) -> None:
        """Отрисовка номеров строк в LineNumberArea."""
        painter = QPainter(self._line_number_area)  # type: ignore[arg-type]
        painter.fillRect(event.rect(), QColor("#f0f0f0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        # Получаем цвет текста из палитры
        palette = self.palette()
        # mypy: color() not in stubs
        dim_color = palette.color(palette.ColorRole.Midlight)  # type: ignore[attr-defined]

        painter.setPen(dim_color)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(
                    0,
                    top,
                    self._line_number_area.width() - 5,  # type: ignore[union-attr]
                    round(self.blockBoundingRect(block).height()),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

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
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText("\n")
            return True

        # Проверяем, является ли строка пустой цитатой
        empty_bq = _is_empty_blockquote(text)

        if empty_bq is not None:
            # Пустая цитата — завершаем цитату
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
                prefix_parts.append(f"{bq_info[1]}{marker}")
            else:
                prefix_parts.append(f"{indent}{marker}")
        elif bq_info:
            prefix_parts.append(f"{bq_info[1]}")

        prefix = "".join(prefix_parts)

        cursor.insertText("\n")
        cursor.insertText(prefix)

        if heading_info:
            cursor.insertText("\n")

        return True
