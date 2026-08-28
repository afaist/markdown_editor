"""Tests for LaTeXProcessor - inline and display math handling."""

from markdown_editor_pkg.latex_processor import LaTeXProcessor


class TestLatexProcessing:
    """Тесты обработки LaTeX-формул через новый LaTeXProcessor."""

    def setup_method(self):
        self.processor = LaTeXProcessor()

    def test_inline_latex_preserved(self):
        """Тест: встроенные формулы $...$ заменяются на плейсхолдеры."""
        text = "Формула: $a^2 + b^2 = c^2$"
        processed = self.processor.process(text)

        assert "<!-- inline-math-0 -->" in processed
        assert "a^2 + b^2 = c^2" in self.processor.inline_math_cache

    def test_block_latex_preserved(self):
        """Тест: блочные формулы $$...$$ заменяются на плейсхолдеры."""
        text = "$$\\int_0^1 x^2 dx$$"
        processed = self.processor.process(text)

        assert "<!-- display-math-0 -->" in processed
        assert "\\int_0^1 x^2 dx" in self.processor.display_math_cache

    def test_multiple_formulas(self):
        """Тест: несколько формул разных типов."""
        text = "$a$ и $b$ и $$c$$"
        processed = self.processor.process(text)

        assert "<!-- inline-math-0 -->" in processed
        assert "<!-- inline-math-1 -->" in processed
        assert "<!-- display-math-0 -->" in processed

        assert len(self.processor.inline_math_cache) == 2
        assert len(self.processor.display_math_cache) == 1
        assert "a" in self.processor.inline_math_cache[0]
        assert "b" in self.processor.inline_math_cache[1]
        assert "c" in self.processor.display_math_cache[0]

    def test_latex_with_nested_sup_sub(self):
        """Тест: формулы со степенями и индексами."""
        text = "$E = mc^2$ и $x_1 + x_2$"
        processed = self.processor.process(text)
        assert "E = mc^2" in self.processor.inline_math_cache[0]
        assert "x_1 + x_2" in self.processor.inline_math_cache[1]

    def test_process_no_latex(self):
        """Текст без формул не меняется."""
        text = "Просто текст без формул"
        processed = self.processor.process(text)
        assert processed == text
        assert len(self.processor.inline_math_cache) == 0
        assert len(self.processor.display_math_cache) == 0

    def test_restore_display_empty_cache(self):
        """Восстановление display при пустом кэше возвращает плейсхолдер."""
        text = "<!-- display-math-0 -->"
        result = self.processor.restore_display(text)
        assert "<!-- display-math-0 -->" in result

    def test_restore_inline_empty_cache(self):
        """Восстановление inline при пустом кэше возвращает плейсхолдер."""
        text = "<!-- inline-math-0 -->"
        result = self.processor.restore_inline(text)
        assert "<!-- inline-math-0 -->" in result

    def test_reset_clears_caches(self):
        """Сброс очищает кэши."""
        self.processor.process("$a$")
        assert len(self.processor.inline_math_cache) == 1
        self.processor.reset()
        assert len(self.processor.inline_math_cache) == 0
        assert len(self.processor.display_math_cache) == 0

    def test_latex_with_html_tags_inside(self):
        """Формулы с HTML-тегами внутри."""
        text = "$a < b$ и $c > d$"
        processed = self.processor.process(text)
        assert "<!-- inline-math-0 -->" in processed
        assert "a < b" in self.processor.inline_math_cache[0]
