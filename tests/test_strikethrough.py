"""Tests for strikethrough processing."""

from markdown_editor_pkg.latex_processor import StrikethroughProcessor


class TestStrikethroughProcessor:
    """Тесты зачёркивания."""

    def test_strikethrough(self):
        """~~text~~ заменяется на <del>text</del>."""
        sp = StrikethroughProcessor()

        html = "Это <b>~~зачёркнуто~~</b> текст"
        result = sp.apply(html)
        assert "<del>зачёркнуто</del>" in result

    def test_strikethrough_protects_code(self):
        """~~ внутри <code> и <pre> не меняется."""
        sp = StrikethroughProcessor()

        html = "<code>~~код~~</code> и ~~реальный~~"
        result = sp.apply(html)
        assert "<code>~~код~~</code>" in result
        assert "<del>реальный</del>" in result
