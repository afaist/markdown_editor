"""Tests for PDF headers/footers in markdown rendering."""

from markdown_editor_pkg.editor import MarkdownEditorPyQt


class TestPdfHeaders:
    """Тесты колонтитулов при экспорте в PDF."""

    def setup_method(self):
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def teardown_method(self):
        self.editor.close()

    def test_render_with_headers(self):
        """Рендеринг с колонтитулами включает page-header и page-footer."""
        headers = {
            "show_headers": True,
            "header_text": "TestDoc.md",
            "footer_text": "Страница {page}",
        }
        html = self.editor.renderer.render(
            "# Hello",
            theme_name="light",
            headers=headers,
        )
        assert 'class="page-header"' in html
        assert 'class="page-footer"' in html
        assert "TestDoc.md" in html
        assert 'Страница {PAGE_NUM}' in html

    def test_render_without_headers(self):
        """Рендеринг без колонтитулов не включает page-header/footer."""
        html = self.editor.renderer.render(
            "# Hello",
            theme_name="light",
            headers={"show_headers": False},
        )
        assert '<div class="page-header">' not in html
        assert '<div class="page-footer">' not in html

    def test_render_default_no_headers(self):
        """Рендеринг без параметра headers не включает колонтитулы."""
        html = self.editor.renderer.render(
            "# Hello",
            theme_name="light",
        )
        assert 'class="page-header"' not in html
        assert 'class="page-footer"' not in html

    def test_pdf_headers_in_print_styles(self):
        """PRINT_STYLES_TEMPLATE содержит стили для колонтитулов."""
        template = self.editor.renderer.PRINT_STYLES_TEMPLATE
        assert ".page-header" in template
        assert ".page-footer" in template
        assert "position: fixed" in template
        assert "@media print" in template

    def test_pdf_headers_no_css_page_center(self):
        """PRINT_STYLES_TEMPLATE не содержит нерабочие @top-center."""
        template = self.editor.renderer.PRINT_STYLES_TEMPLATE
        assert "@top-center" not in template
        assert "@bottom-center" not in template

    def test_page_count_js_injected_with_placeholder(self):
        """JS для нумерации страниц добавляется при наличии {page} в footer."""
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
        assert "scrollHeight" in html
        assert "totalPages" in html
        assert "page-footer" in html
