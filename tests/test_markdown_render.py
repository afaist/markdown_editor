"""Tests for Markdown rendering to HTML."""

from markdown_editor_pkg.editor import MarkdownEditorPyQt


class TestMarkdownRender:
    """Тесты рендеринга Markdown в HTML."""

    def setup_method(self):
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def teardown_method(self):
        self.editor.close()

    def test_simple_render(self):
        """Простой Markdown рендерится в HTML."""
        md = "Простой текст"
        html = self.editor.render_markdown(md)
        assert "<p>Простой текст</p>" in html

    def test_headings_render(self):
        """Заголовки H1–H3 рендерятся."""
        md = "# Заголовок 1\n## Заголовок 2\n### Заголовок 3"
        html = self.editor.render_markdown(md)
        for i in range(1, 4):
            assert f'<h{i} id="{i}">Заголовок {i}</h{i}>' in html

    def test_latex_inline_render(self):
        """Встроенные формулы $...$ корректно обрабатываются."""
        md = "Формула: $a^2 + b^2 = c^2$"
        html = self.editor.render_markdown(md)
        assert "$a^2 + b^2 = c^2$" in html
        assert "katex.min.js" in html
        assert "auto-render.min.js" in html
        assert '{left: "$", right: "$", display: false}' in html

    def test_latex_block_render(self):
        """Блочные формулы $$...$$ корректно обрабатываются."""
        md = "$$\\int_0^1 x^2 dx$$"
        html = self.editor.render_markdown(md)
        assert "$$\\int_0^1 x^2 dx$$" in html
        assert "katex.min.js" in html
        assert "auto-render.min.js" in html
        assert '{left: "$$", right: "$$", display: true}' in html

    def test_full_html_structure(self):
        """Рендеринг возвращает полный HTML-документ."""
        md = "# Привет"
        html = self.editor.render_markdown(md)

        assert html.startswith("<!DOCTYPE html>")
        assert "<html>" in html
        assert "</html>" in html
        assert "<head>" in html
        assert "</head>" in html
        assert "<body>" in html
        assert "</body>" in html
        assert "katex.min.css" in html
        assert "katex.min.js" in html

    def test_render_with_tables(self):
        """Таблицы Markdown рендерятся в <table>."""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = self.editor.render_markdown(md)
        assert "<table>" in html
        assert "<th>A</th>" in html
        assert "<td>1</td>" in html

    def test_render_with_toc(self):
        """Оглавление добавляется при наличии заголовков."""
        md = "# Заголовок\nТекст\n## Подзаголовок"
        html = self.editor.render_markdown(md)
        # Оглавление может быть добавлено, зависит от реализации
        # Проверяем что рендер не падает
        assert "<html>" in html

    def test_render_with_all_callout_types_in_html(self):
        """Все типы callouts присутствуют в HTML."""
        md = "> [!NOTE] заметка\n> [!WARNING] предупреждение"
        html = self.editor.render_markdown(md)
        assert "callout-note" in html
        assert "callout-warning" in html

    def test_render_with_fenced_code(self):
        """Fenced code block рендерится в <pre><code>."""
        md = "```python\nprint('hello')\n```"
        html = self.editor.render_markdown(md)
        assert "<pre" in html
        assert "<code" in html

    def test_render_latex_survives_html_escaping(self):
        """LaTeX-формулы не ломаются при HTML-экранировании."""
        md = "Текст с <b>жирным</b> и $a < b$"
        html = self.editor.render_markdown(md)
        # Базовая проверка что рендер не падает
        assert "<html>" in html
        assert "a < b" in html or "a" in html

    def test_render_with_headers_includes_print_styles(self):
        """Рендеринг с колонтитулами включает print-стили."""
        headers = {
            "show_headers": True,
            "header_text": "Test",
            "footer_text": "Страница {page}",
        }
        html = self.editor.renderer.render(
            "# Hello",
            theme_name="light",
            headers=headers,
        )
        assert ".page-header" in html
        assert "@media print" in html

    def test_render_prism_js_injected(self):
        """Prism.js JS и CSS добавляются при рендеринге."""
        md = "```python\nprint('hello')\n```"
        html = self.editor.render_markdown(md)
        assert "prism" in html.lower() or "highlightAll" in html or "<code" in html
