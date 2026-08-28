"""Tests for PrismJSProcessor."""

from markdown_editor_pkg.prism_processor import PrismJSProcessor


class TestPrismJSProcessor:
    """Тесты PrismJSProcessor."""

    def setup_method(self):
        self.processor = PrismJSProcessor()

    def test_prism_languages_list(self):
        """Список поддерживаемых языков содержит 10 языков."""
        assert len(self.processor.PRISM_LANGUAGES) == 10
        assert "python" in self.processor.PRISM_LANGUAGES
        assert "javascript" in self.processor.PRISM_LANGUAGES
        assert "rust" in self.processor.PRISM_LANGUAGES or "cpp" in self.processor.PRISM_LANGUAGES

    def test_get_prism_css_path_light(self):
        """Для light темы возвращается prism-okaidia.min.css."""
        path = self.processor.get_prism_css_path("light")
        assert "prism-okaidia.min.css" in path

    def test_get_prism_css_path_dark(self):
        """Для dark темы возвращается prism-tomorrow.min.css."""
        path = self.processor.get_prism_css_path("dark")
        assert "prism-tomorrow.min.css" in path

    def test_get_prism_css_path_contrast(self):
        """Для contrast темы возвращается fallback (okaidia)."""
        path = self.processor.get_prism_css_path("contrast")
        assert "prism-okaidia.min.css" in path

    def test_get_prism_js_components(self):
        """get_prism_js_components возвращает список путей."""
        components = self.processor.get_prism_js_components()
        assert len(components) == 10
        assert any("prism-python.min.js" in c for c in components)
        assert any("prism-javascript.min.js" in c for c in components)

    def test_inject_prism_adds_css_to_head(self):
        """inject_prism добавляет CSS в <head>."""
        html = "<html><head></head><body></body></html>"
        result = self.processor.inject_prism(html, "light", "/base")
        assert "prism-okaidia.min.css" in result
        assert "<link" in result

    def test_inject_prism_adds_js_to_body(self):
        """inject_prism добавляет JS в <body>."""
        html = "<html><head></head><body></body></html>"
        result = self.processor.inject_prism(html, "light", "/base")
        assert "prism.min.js" in result
        assert "highlightAll" in result

    def test_inject_prism_call_highlightAll(self):
        """inject_prism вызывает Prism.highlightAll()."""
        html = "<html><head></head><body></body></html>"
        result = self.processor.inject_prism(html, "light", "/base")
        assert "Prism.highlightAll()" in result
