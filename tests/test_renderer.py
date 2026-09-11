"""Tests for MarkdownRenderer internals."""

from markdown_editor_pkg.callout_processor import CalloutProcessor
from markdown_editor_pkg.latex_processor import StrikethroughProcessor
from markdown_editor_pkg.markdown_renderer import MarkdownRenderer
from markdown_editor_pkg.themes import ThemesManager


class TestStrikethroughProcessor:
    """Тесты зачёркивания с защитой блоков кода."""

    def setup_method(self):
        self.sp = StrikethroughProcessor()

    def test_basic_strikethrough(self):
        """Обычное ~~text~~ заменяется на <del>."""
        result = self.sp.apply("~~deleted~~")
        assert "<del>deleted</del>" in result

    def test_strikethrough_protected_in_code_tag(self):
        """~~ внутри <code> не заменяется."""
        result = self.sp.apply("<code>~~safe~~</code>")
        assert "<code>~~safe~~</code>" in result
        assert "<del>" not in result

    def test_strikethrough_protected_in_pre_tag(self):
        """~~ внутри <pre> не заменяется."""
        result = self.sp.apply("<pre>~~safe~~</pre>")
        assert "<pre>~~safe~~</pre>" in result
        assert "<del>" not in result

    def test_strikethrough_with_newlines_in_pre(self):
        """~~ внутри <pre> с несколькими строками не заменяется."""
        html = "<pre>\nline 1\n~~safe~~\nline 3\n</pre>"
        result = self.sp.apply(html)
        assert "<del>" not in result

    def test_multiple_strikethrough(self):
        """Несколько зачёркиваний обрабатываются."""
        result = self.sp.apply("~~a~~ and ~~b~~")
        assert result.count("<del>") == 2
        assert result.count("</del>") == 2


class TestCalloutProcessor:
    """Тесты обработки GitHub Callouts."""

    def setup_method(self):
        self.cp = CalloutProcessor()

    def test_note_callout(self):
        """[!NOTE] преобразуется в callout-note div."""
        html = "<blockquote><p>[!NOTE] This is a note</p></blockquote>"
        result = self.cp.process(html)
        assert 'class="callout callout-note"' in result

    def test_callout_marker_stripped(self):
        """Маркер [!TYPE] удаляется из тела callout."""
        html = "<blockquote><p>[!NOTE] Body text</p></blockquote>"
        result = self.cp.process(html)
        assert "[!NOTE]" not in result

    def test_tip_callout(self):
        """[!TIP] преобразуется в callout-tip."""
        html = "<blockquote><p>[!TIP] A tip here</p></blockquote>"
        result = self.cp.process(html)
        assert 'class="callout callout-tip"' in result

    def test_multiple_paragraphs_same_callout(self):
        """Несколько параграфов без маркера объединяются в один callout."""
        html = "<blockquote><p>[!WARNING] First para</p><p>Second para no marker</p></blockquote>"
        result = self.cp.process(html)
        assert result.count('class="callout callout-warning"') == 1

    def test_non_callout_blockquote_unchanged(self):
        """Обычный blockquote без [!TYPE] не меняется."""
        html = "<blockquote><p>Just a regular quote</p></blockquote>"
        result = self.cp.process(html)
        assert 'class="callout' not in result

    def test_unmatched_callout_type(self):
        """Неизвестный тип [!FOO] не считается callout."""
        html = "<blockquote><p>[!FOO] unknown</p></blockquote>"
        result = self.cp.process(html)
        assert 'class="callout' not in result

    def test_callout_types_set(self):
        """Доступные типы callout."""
        expected = {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}
        assert expected == self.cp.CALLOUT_TYPES


class TestMarkdownRendererPipeline:
    """Тесты пайплайна MarkdownRenderer."""

    def setup_method(self):
        self.tm = ThemesManager()
        self.renderer = MarkdownRenderer(self.tm)

    def test_render_basic_markdown(self):
        """Базовый markdown конвертируется в HTML."""
        html = self.renderer.render("# Hello")
        assert "<h1" in html
        assert ">Hello</h1>" in html

    def test_render_inline_code(self):
        """Встроенный код сохраняется как <code>."""
        html = self.renderer.render("Use `code` here")
        assert "<code>code</code>" in html

    def test_render_table(self):
        """Markdown-таблица преобразуется в HTML table."""
        html = self.renderer.render("| A | B |\n|---|---|\n| 1 | 2 |")
        assert "<table" in html
        assert "<th>A</th>" in html
        assert "<th>B</th>" in html

    def test_strikethrough_in_pipeline(self):
        """Зачёркивание работает в полном пайплайне."""
        html = self.renderer.render("~~deleted~~")
        assert "<del>deleted</del>" in html

    def test_latex_preserved_in_pipeline(self):
        """LaTeX-формулы восстанавливаются в HTML."""
        html = self.renderer.render("Value is $x + y$")
        assert "$x + y$" in html

    def test_display_math_in_pipeline(self):
        """Блочные формулы $$ восстанавливаются."""
        html = self.renderer.render("$$a^2 + b^2$$")
        assert "$$a^2 + b^2$$" in html

    def test_callouts_in_pipeline(self):
        """Callouts обрабатываются в полном пайплайне."""
        md = "> [!NOTE]\n> This is a note"
        html = self.renderer.render(md)
        assert 'class="callout callout-note"' in html
        assert "[!NOTE]" not in html

    def test_render_structure_has_doctype(self):
        """Рендеринг содержит DOCTYPE и базовую структуру."""
        html = self.renderer.render("# Test")
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "</html>" in html

    def test_render_contains_katex_css(self):
        """Рендеринг включает ссылку на KaTeX CSS."""
        html = self.renderer.render("# Test")
        assert "katex.min.css" in html

    def test_render_contains_katex_js(self):
        """Рендеринг включает скрипты KaTeX."""
        html = self.renderer.render("# Test")
        assert "katex.min.js" in html
        assert "auto-render.min.js" in html


class TestMarkdownRendererHelpers:
    """Тесты вспомогательных статических методов MarkdownRenderer."""

    def setup_method(self):
        self.tm = ThemesManager()
        self.renderer = MarkdownRenderer(self.tm)

    def test_resolve_path_no_base(self):
        """_resolve_path без base_dir возвращает относительный путь."""
        assert self.renderer._resolve_path("", "katex/katex.min.css") == "katex/katex.min.css"

    def test_resolve_path_with_base(self):
        """_resolve_path с base_dir объединяет пути."""
        result = self.renderer._resolve_path("/base", "katex/katex.min.css")
        assert result == "/base/katex/katex.min.css"

    def test_parse_headers_none(self):
        """_parse_headers(None) возвращает выключенные колонтитулы."""
        show, header, footer = self.renderer._parse_headers(None)
        assert show is False
        assert header == ""
        assert footer == ""

    def test_parse_headers_empty_dict(self):
        """_parse_headers({}) возвращает выключенные колонтитулы."""
        show, _header, _footer = self.renderer._parse_headers({})
        assert show is False

    def test_parse_headers_with_values(self):
        """_parse_headers извлекает значения из словаря."""
        headers = {
            "show_headers": True,
            "header_text": "Header Text",
            "footer_text": "Footer Text",
        }
        show, header, footer = self.renderer._parse_headers(headers)
        assert show is True
        assert header == "Header Text"
        assert footer == "Footer Text"

    def test_build_header_footer_disabled(self):
        """_build_header_footer(show=False) возвращает пустые строки."""
        h, f = self.renderer._build_header_footer(False, "H", "F")
        assert h == ""
        assert f == ""

    def test_build_header_footer_enabled(self):
        """_build_header_footer(show=True) создаёт HTML."""
        h, f = self.renderer._build_header_footer(True, "MyHeader", "MyFooter {page}")
        assert '<div class="page-header">MyHeader</div>' in h
        assert '<div class="page-footer">MyFooter {PAGE_NUM}</div>' in f

    def test_build_page_numbering_js_disabled(self):
        """_build_page_numbering_js(False) возвращает пустую строку."""
        result = MarkdownRenderer._build_page_numbering_js(False)
        assert result == ""

    def test_build_page_numbering_js_enabled(self):
        """_build_page_numbering_js(True) создаёт скрипт."""
        result = MarkdownRenderer._build_page_numbering_js(True)
        assert "<script>" in result
        assert "page-footer" in result
        assert "print-page" in result
        assert "PAGE_NUM" in result

    def test_build_page_numbering_js_no_footers(self):
        """JS нумерации страниц корректно обрабатывает отсутствие footers."""
        result = MarkdownRenderer._build_page_numbering_js(True)
        # Должен содержать querySelectorAll для .page-footer
        assert ".page-footer" in result

    def test_render_preserves_newlines_in_code(self):
        """Фенс-код сохраняет внутренние переносы строк."""
        md = "```\nline1\nline2\nline3\n```"
        html = self.renderer.render(md)
        assert "line1" in html
        assert "line2" in html
        assert "line3" in html

    def test_render_mixed_latex_and_callouts(self):
        """Совместное использование LaTeX и Callouts работает."""
        md = "> [!NOTE]\n> Value is $x + y$\n"
        html = self.renderer.render(md)
        assert "$$x + y$$" not in html
        assert "$x + y$" in html
        assert 'class="callout callout-note"' in html

    def test_render_with_complex_latex(self):
        """Сложные LaTeX-выражения сохраняются."""
        md = "Formula: $$\\frac{a}{b}$$ and $\\alpha + \\beta$"
        html = self.renderer.render(md)
        assert "$$\\frac{a}{b}$$" in html
        assert "$\\alpha + \\beta$" in html

    def test_print_styles_template_contains_callout_styles(self):
        """Шаблон print_styles содержит стили для callout."""
        from markdown_editor_pkg.markdown_renderer import _PRINT_STYLES_TEMPLATE

        template = _PRINT_STYLES_TEMPLATE
        assert ".callout" in template
        assert ".callout-note" in template
        assert ".callout-tip" in template
        assert ".callout-important" in template
        assert ".callout-warning" in template
        assert ".callout-caution" in template

    def test_print_styles_contains_media_print(self):
        """Шаблон print_styles содержит @media print."""
        from markdown_editor_pkg.markdown_renderer import _PRINT_STYLES_TEMPLATE

        template = _PRINT_STYLES_TEMPLATE
        assert "@media print" in template
        assert "@page" in template

    def test_render_empty_text(self):
        """Рендеринг пустого текста создаёт валидный HTML."""
        html = self.renderer.render("")
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html

    def test_render_html_entities_escaped(self):
        """HTML-символы экранируются."""
        html = self.renderer.render("A < B > C")
        assert "&lt;" in html or "<" in html
        assert "&gt;" in html or ">" in html
