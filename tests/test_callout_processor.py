"""Tests for GitHub Callouts processing."""

from markdown_editor_pkg.callout_processor import CalloutProcessor


class TestCalloutProcessor:
    """Тесты GitHub Callouts."""

    def test_callout_detection(self):
        """Callout-маркеры распознаются из blockquote."""
        cp = CalloutProcessor()

        html = "<blockquote><p>[!NOTE] Это заметка</p><p>Продолжение</p></blockquote>"
        result = cp.process(html)

        assert 'class="callout callout-note"' in result
        assert "Это заметка" in result

    def test_normal_blockquote_unchanged(self):
        """Обычный blockquote без маркера не меняется."""
        cp = CalloutProcessor()

        html = "<blockquote><p>Просто цитата</p></blockquote>"
        result = cp.process(html)

        assert "<blockquote>" in result

    def test_all_callout_types(self):
        """Все типы callouts (NOTE, TIP, IMPORTANT, WARNING, CAUTION)."""
        cp = CalloutProcessor()

        for callout_type in ["NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"]:
            html = f"<blockquote><p>[!{callout_type}] Тест</p></blockquote>"
            result = cp.process(html)
            assert f"callout-{callout_type.lower()}" in result

    def test_multiple_callouts_in_one_blockquote(self):
        """Несколько callouts в одном blockquote."""
        cp = CalloutProcessor()

        html = (
            "<blockquote><p>[!NOTE] Первая заметка</p><p>[!WARNING] Предупреждение</p></blockquote>"
        )
        result = cp.process(html)
        assert "callout-note" in result
        assert "callout-warning" in result

    def test_callout_with_multiple_paragraphs(self):
        """Callout с несколькими абзацами."""
        cp = CalloutProcessor()

        html = (
            "<blockquote><p>[!NOTE] Заголовок</p>"
            "<p>Первый абзац</p><p>Второй абзац</p></blockquote>"
        )
        result = cp.process(html)
        assert "callout-note" in result
        assert "Первый абзац" in result
        assert "Второй абзац" in result

    def test_callout_case_insensitive(self):
        """Callout-маркеры регистронезависимы."""
        cp = CalloutProcessor()

        for variant in ["[!note]", "[!Note]", "[!NOTE]"]:
            html = f"<blockquote><p>{variant} Тест</p></blockquote>"
            result = cp.process(html)
            assert "callout-note" in result

    def test_mixed_blockquote_and_callout(self):
        """Смешанные blockquote и callouts."""
        cp = CalloutProcessor()

        html = (
            "<p>Обычный текст</p>"
            "<blockquote><p>[!NOTE] Callout</p></blockquote>"
            "<blockquote><p>Обычная цитата</p></blockquote>"
        )
        result = cp.process(html)
        assert "callout-note" in result
        # Обычный blockquote должен остаться без изменений
        assert "<blockquote>" in result
