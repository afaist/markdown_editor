"""Tests for TextInsertions."""

from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QTextEdit


class TestTextInsertions:
    """Тесты вставок текста и форматирования."""

    def _create_mock_editor(self):
        """Создаёт mock-объект editor с QTextEdit."""
        text_edit = QTextEdit()
        text_edit.setPlainText("Текст для тестирования")

        class MockEditor:
            def __init__(self, te):
                self.editor = te
                self.current_file = None
                self.is_dirty = False

            def update_preview(self):
                pass

        return MockEditor(text_edit)

    def test_insert_bold_no_selection(self):
        """Вставка жирного без выделения."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        # cursor = mock.editor.textCursor()
        # cursor.select(cursor.SelectionType.Document)
        # mock.editor.setTextCursor(cursor)

        ti.insert_bold()
        text = mock.editor.toPlainText()
        assert "**text**" in text

    def test_insert_bold_with_selection(self):
        """Вставка жирного с выделением текста."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(5, QTextCursor.MoveMode.KeepAnchor)
        mock.editor.setTextCursor(cursor)

        ti.insert_bold()
        text = mock.editor.toPlainText()
        # Выделенный текст "Текст" должен быть обернут в **
        assert "**Текст**" in text

    def test_insert_italic_no_selection(self):
        """Вставка курсива без выделения."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_italic()
        text = mock.editor.toPlainText()
        assert "*text*" in text

    def test_insert_italic_with_selection(self):
        """Вставка курсива с выделением текста."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(5, QTextCursor.MoveMode.KeepAnchor)
        mock.editor.setTextCursor(cursor)

        ti.insert_italic()
        text = mock.editor.toPlainText()
        assert "*Текст*" in text

    def test_insert_strikethrough(self):
        """Вставка зачёркнутого текста."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_strikethrough()
        text = mock.editor.toPlainText()
        assert "~~text~~" in text

    def test_insert_inline_code(self):
        """Вставка встроенного кода."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_inline_code()
        text = mock.editor.toPlainText()
        assert "`code`" in text

    def test_insert_unordered_list_no_selection(self):
        """Вставка маркированного списка без выделения."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_unordered_list()
        text = mock.editor.toPlainText()
        assert "- list item" in text

    def test_insert_unordered_list_with_selection(self):
        """Вставка маркированного списка с выделением."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(11, QTextCursor.MoveMode.KeepAnchor)  # "Текст для "
        mock.editor.setTextCursor(cursor)

        ti.insert_unordered_list()
        text = mock.editor.toPlainText()
        assert "- Текст для " in text

    def test_insert_ordered_list(self):
        """Вставка нумерованного списка."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_ordered_list()
        text = mock.editor.toPlainText()
        assert "1. list item" in text

    def test_insert_task_list(self):
        """Вставка элемента списка задач."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_task_list()
        text = mock.editor.toPlainText()
        assert "- [ ] task" in text

    def test_insert_heading_level_1(self):
        """Вставка заголовка H1."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_heading(1)
        text = mock.editor.toPlainText()
        assert "# " in text

    def test_insert_heading_level_7(self):
        """Вставка заголовка H7."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_heading(7)
        text = mock.editor.toPlainText()
        assert "####### " in text

    def test_insert_heading_invalid_level(self):
        """Невалидный уровень заголовка игнорируется."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        initial = mock.editor.toPlainText()
        ti.insert_heading(0)  # невалидно
        ti.insert_heading(8)  # невалидно
        text = mock.editor.toPlainText()
        assert text == initial

    def test_insert_blockquote(self):
        """Вставка цитаты."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_blockquote()
        text = mock.editor.toPlainText()
        assert "> " in text

    def test_insert_code_block_python(self):
        """Вставка блока кода с языком Python."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_code_block("python")
        text = mock.editor.toPlainText()
        assert "```python" in text
        assert "```" in text

    def test_insert_code_block_generic(self):
        """Вставка блока кода без языка."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_code_block()
        text = mock.editor.toPlainText()
        assert "```\n\n```" in text

    def test_insert_latex_fraction(self):
        """Вставка LaTeX дробной функции."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_latex_fraction()
        text = mock.editor.toPlainText()
        assert "\\frac{}{}" in text

    def test_insert_latex_matrix(self):
        """Вставка LaTeX матрицы."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_latex_matrix()
        text = mock.editor.toPlainText()
        assert "\\begin{matrix}" in text
        assert "\\end{matrix}" in text

    def test_insert_horizontal_rule(self):
        """Вставка горизонтального разделителя."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_horizontal_rule()
        text = mock.editor.toPlainText()
        assert "---" in text

    def test_insert_table(self):
        """Вставка таблицы Markdown."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_table()
        text = mock.editor.toPlainText()
        assert "| Column 1 | Column 2 | Column 3 |" in text
        assert "|-----------|-----------|----------|" in text

    def test_insert_html_comment(self):
        """Вставка HTML-комментария."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_html_comment()
        text = mock.editor.toPlainText()
        assert "<!-- " in text
        assert " -->" in text

    def test_insert_inline_latex_no_selection(self):
        """Вставка inline LaTeX без выделения."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_inline_latex()
        text = mock.editor.toPlainText()
        assert "$$" in text

    def test_insert_block_latex_no_selection(self):
        """Вставка блочного LaTeX без выделения."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_block_latex()
        text = mock.editor.toPlainText()
        assert "$$" in text

    def test_insert_latex_superscript(self):
        """Вставка LaTeX надстрочного индекса."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_latex_superscript()
        text = mock.editor.toPlainText()
        assert "^{}" in text

    def test_insert_latex_subscript(self):
        """Вставка LaTeX подстрочного индекса."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_latex_subscript()
        text = mock.editor.toPlainText()
        assert "_{}" in text

    def test_insert_latex_sum(self):
        """Вставка LaTeX суммы."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_latex_sum()
        text = mock.editor.toPlainText()
        assert "\\sum_{}^{}" in text

    def test_insert_latex_integral(self):
        """Вставка LaTeX интеграла."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_latex_integral()
        text = mock.editor.toPlainText()
        assert "\\int_{}^{}" in text

    def test_insert_latex_sqrt(self):
        """Вставка LaTeX квадратного корня."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_latex_sqrt()
        text = mock.editor.toPlainText()
        assert "\\sqrt{}" in text

    def test_insert_link_with_mock(self):
        """Вставка ссылки с mock QInputDialog."""
        from unittest.mock import patch

        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        with patch("markdown_editor_pkg.text_insertions.QInputDialog.getText") as mock_input:
            mock_input.side_effect = [
                ("https://example.com", True),  # URL
                ("Пример", True),  # Текст ссылки
            ]
            ti.insert_link()

            text = mock.editor.toPlainText()
            assert "[Пример](https://example.com)" in text

    def test_insert_link_cancel_url(self):
        """Отмена ввода URL отменяет вставку ссылки."""
        from unittest.mock import patch

        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        mock.editor.setPlainText("Исходный текст")
        ti = TextInsertions(mock)

        with patch("markdown_editor_pkg.text_insertions.QInputDialog.getText") as mock_input:
            mock_input.return_value = ("", False)  # Отмена
            ti.insert_link()

        text = mock.editor.toPlainText()
        assert text == "Исходный текст"

    def test_insert_image_with_mock(self):
        """Вставка изображения с mock QFileDialog."""
        from unittest.mock import patch

        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        with patch("markdown_editor_pkg.text_insertions.QFileDialog.getOpenFileName") as mock_file:
            mock_file.return_value = ("/path/to/image.png", "")
            ti.insert_image()

        text = mock.editor.toPlainText()
        assert "![image](/path/to/image.png)" in text

    def test_insert_image_cancel(self):
        """Отмена выбора изображения отменяет вставку."""
        from unittest.mock import patch

        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        mock.editor.setPlainText("Исходный текст")
        ti = TextInsertions(mock)

        with patch("markdown_editor_pkg.text_insertions.QFileDialog.getOpenFileName") as mock_file:
            mock_file.return_value = ("", "")  # Отмена
            ti.insert_image()

        text = mock.editor.toPlainText()
        assert text == "Исходный текст"

    def test_insert_image_windows_path(self):
        """Вставка изображения с Windows-путём — экранирование слешей."""
        from unittest.mock import patch

        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        with patch("markdown_editor_pkg.text_insertions.QFileDialog.getOpenFileName") as mock_file:
            mock_file.return_value = (r"C:\Users\img.png", "")
            ti.insert_image()

    def test_insert_ordered_list_with_selection(self):
        """Вставка нумерованного списка с выделением текста."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(11, QTextCursor.MoveMode.KeepAnchor)  # "Текст для "
        mock.editor.setTextCursor(cursor)

        ti.insert_ordered_list()
        text = mock.editor.toPlainText()
        assert "1. Текст для " in text

    def test_insert_inline_latex_with_selection(self):
        """Вставка inline LaTeX с выделением текста."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        mock.editor.setPlainText("Formula E=mc2 here")
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.setPosition(8)  # начало "E=mc2"
        cursor.setPosition(13, QTextCursor.MoveMode.KeepAnchor)  # "E=mc2"
        mock.editor.setTextCursor(cursor)

        ti.insert_inline_latex()
        text = mock.editor.toPlainText()
        assert "$E=mc2$" in text

    def test_insert_block_latex_with_selection(self):
        """Вставка блочного LaTeX с выделением текста."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        mock.editor.setPlainText("Formula E=mc2 here")
        ti = TextInsertions(mock)

        cursor = mock.editor.textCursor()
        cursor.setPosition(8)  # начало "E=mc2"
        cursor.setPosition(13, QTextCursor.MoveMode.KeepAnchor)  # "E=mc2"
        mock.editor.setTextCursor(cursor)

        ti.insert_block_latex()
        text = mock.editor.toPlainText()
        assert "\n$$\nE=mc2\n$$" in text
