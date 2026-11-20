"""Tests for line number area feature."""

from markdown_editor_pkg.editor_keypress import MarkdownTextEdit


def test_line_numbers_default_off():
    """Номера строк по умолчанию выключены."""
    widget = MarkdownTextEdit()
    assert widget.is_show_line_numbers() is False
    widget.deleteLater()


def test_line_numbers_toggle_on():
    """Включение номеров строк."""
    widget = MarkdownTextEdit()
    widget.set_show_line_numbers(True)
    assert widget.is_show_line_numbers() is True
    assert widget.line_number_area_width() > 0
    widget.deleteLater()


def test_line_numbers_toggle_off():
    """Выключение номеров строк."""
    widget = MarkdownTextEdit()
    widget.set_show_line_numbers(True)
    widget.set_show_line_numbers(False)
    assert widget.is_show_line_numbers() is False
    assert widget.line_number_area_width() == 0
    widget.deleteLater()


def test_line_numbers_toggle_same_state_noop():
    """Повторное переключение в то же состояние — noop."""
    widget = MarkdownTextEdit()
    widget.set_show_line_numbers(True)
    width1 = widget.line_number_area_width()
    widget.set_show_line_numbers(True)  # Повторно включаем
    width2 = widget.line_number_area_width()
    assert width1 == width2
    widget.deleteLater()


def test_line_numbers_area_width_when_off():
    """Ширина области номеров строк = 0 когда выключены."""
    widget = MarkdownTextEdit()
    assert widget.line_number_area_width() == 0
    widget.deleteLater()


def test_line_numbers_area_width_when_on():
    """Ширина области номеров строк > 0 когда включены."""
    widget = MarkdownTextEdit()
    widget.set_show_line_numbers(True)
    width = widget.line_number_area_width()
    assert width > 0
    widget.deleteLater()


def test_line_numbers_width_scales_with_block_count():
    """Ширина увеличивается с количеством блоков."""
    widget = MarkdownTextEdit()
    widget.set_show_line_numbers(True)

    # Добавляем много строк
    lines = "\n".join(f"Line {i}" for i in range(1, 10000))
    widget.setPlainText(lines)

    width = widget.line_number_area_width()
    assert width > 0
    widget.deleteLater()


def test_line_numbers_not_in_text():
    """Номера строк не являются частью текста."""
    widget = MarkdownTextEdit()
    widget.setPlainText("Hello\nWorld")
    widget.set_show_line_numbers(True)
    assert widget.toPlainText() == "Hello\nWorld"
    assert "1" not in widget.toPlainText()
    widget.deleteLater()


def test_line_numbers_with_many_blocks():
    """Корректная ширина при большом количестве блоков."""
    widget = MarkdownTextEdit()
    widget.setPlainText("\n".join(f"Line {i}" for i in range(1, 10000)))
    widget.set_show_line_numbers(True)
    width = widget.line_number_area_width()
    assert width > 0
    widget.deleteLater()
