# test_markdown_editor.py
# Updated Markdown Editor Tests (PyQt6-based)
# Работает с разбитым на пакеты кодом

import unittest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import QtWebEngineWidgets first to satisfy Qt requirements
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication

app = QApplication.instance()


class TestLatexProcessing(unittest.TestCase):
    """Тесты обработки LaTeX-формул через новый LaTeXProcessor."""

    def setUp(self):
        from markdown_editor_pkg.editor import MarkdownEditorPyQt
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def tearDown(self):
        self.editor.close()
        del self.editor

    def test_inline_latex_preserved(self):
        """Тест: встроенные формулы $...$ заменяются на плейсхолдеры."""
        text = "Формула: $a^2 + b^2 = c^2$"
        processed = self.editor.latex_processor.process(text)

        self.assertIn("<!-- inline-math-0 -->", processed)
        self.assertIn("a^2 + b^2 = c^2", self.editor.latex_processor.inline_math_cache)

    def test_block_latex_preserved(self):
        """Тест: блочные формулы $$...$$ заменяются на плейсхолдеры."""
        text = "$$\\int_0^1 x^2 dx$$"
        processed = self.editor.latex_processor.process(text)

        self.assertIn("<!-- display-math-0 -->", processed)
        self.assertIn("\\int_0^1 x^2 dx", self.editor.latex_processor.display_math_cache)

    def test_multiple_formulas(self):
        """Тест: несколько формул разных типов."""
        text = "$a$ и $b$ и $$c$$"
        processed = self.editor.latex_processor.process(text)

        self.assertIn("<!-- inline-math-0 -->", processed)
        self.assertIn("<!-- inline-math-1 -->", processed)
        self.assertIn("<!-- display-math-0 -->", processed)

        self.assertEqual(len(self.editor.latex_processor.inline_math_cache), 2)
        self.assertEqual(len(self.editor.latex_processor.display_math_cache), 1)
        self.assertIn("a", self.editor.latex_processor.inline_math_cache[0])
        self.assertIn("b", self.editor.latex_processor.inline_math_cache[1])
        self.assertIn("c", self.editor.latex_processor.display_math_cache[0])

    def test_latex_with_nested_sup_sub(self):
        """Тест: формулы со степенями и индексами."""
        text = "$E = mc^2$ и $x_1 + x_2$"
        processed = self.editor.latex_processor.process(text)
        self.assertIn("E = mc^2", self.editor.latex_processor.inline_math_cache[0])
        self.assertIn("x_1 + x_2", self.editor.latex_processor.inline_math_cache[1])


class TestThemeSwitching(unittest.TestCase):
    """Тесты переключения тем через ThemesManager."""

    def setUp(self):
        from markdown_editor_pkg.editor import MarkdownEditorPyQt
        self.editor = MarkdownEditorPyQt()

    def tearDown(self):
        self.editor.close()
        del self.editor

    def test_initial_theme_is_light(self):
        """По умолчанию тема предпросмотра — light."""
        self.assertEqual(self.editor.theme_manager.theme_name, "light")

    def test_theme_toggle(self):
        """Переключение темы обновляет theme_name."""
        initial = self.editor.theme_manager.theme_name
        self.editor.theme_manager.toggle_preview_theme()
        self.assertNotEqual(initial, self.editor.theme_manager.theme_name)

        self.editor.theme_manager.toggle_preview_theme()
        self.editor.theme_manager.toggle_preview_theme()
        self.assertEqual(self.editor.theme_manager.theme_name, "light")

    def test_set_theme(self):
        """set_preview_theme устанавливает нужную тему."""
        self.editor.theme_manager.set_preview_theme("dark")
        self.assertEqual(self.editor.theme_manager.theme_name, "dark")
        self.editor.theme_manager.set_preview_theme("contrast")
        self.assertEqual(self.editor.theme_manager.theme_name, "contrast")

    def test_themes_dict_exists(self):
        """Словарь THEMES_CSS содержит все темы."""
        themes = self.editor.theme_manager.THEMES_CSS
        self.assertIn("light", themes)
        self.assertIn("dark", themes)
        self.assertIn("contrast", themes)
        for theme_name, css in themes.items():
            self.assertIsInstance(css, str)
            self.assertGreater(len(css), 0)


class TestMarkdownRender(unittest.TestCase):
    """Тесты рендеринга Markdown в HTML."""

    def setUp(self):
        from markdown_editor_pkg.editor import MarkdownEditorPyQt
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def tearDown(self):
        self.editor.close()
        del self.editor

    def test_simple_render(self):
        """Простой Markdown рендерится в HTML."""
        md = "Простой текст"
        html = self.editor.render_markdown(md)
        self.assertIn("<p>Простой текст</p>", html)

    def test_headings_render(self):
        """Заголовки H1–H3 рендерятся."""
        md = "# Заголовок 1\n## Заголовок 2\n### Заголовок 3"
        html = self.editor.render_markdown(md)
        for i in range(1, 4):
            self.assertIn(f"<h{i} id=\"{i}\">Заголовок {i}</h{i}>", html)

    def test_latex_inline_render(self):
        """Встроенные формулы $...$ корректно обрабатываются."""
        md = "Формула: $a^2 + b^2 = c^2$"
        html = self.editor.render_markdown(md)
        self.assertIn("$a^2 + b^2 = c^2$", html)
        self.assertIn("katex.min.js", html)
        self.assertIn("auto-render.min.js", html)
        self.assertIn('{left: "$", right: "$", display: false}', html)

    def test_latex_block_render(self):
        """Блочные формулы $$...$$ корректно обрабатываются."""
        md = "$$\\int_0^1 x^2 dx$$"
        html = self.editor.render_markdown(md)
        self.assertIn("$$\\int_0^1 x^2 dx$$", html)
        self.assertIn("katex.min.js", html)
        self.assertIn("auto-render.min.js", html)
        self.assertIn('{left: "$$", right: "$$", display: true}', html)

    def test_full_html_structure(self):
        """Рендеринг возвращает полный HTML-документ."""
        md = "# Привет"
        html = self.editor.render_markdown(md)

        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn("<html>", html)
        self.assertIn("</html>", html)
        self.assertIn("<head>", html)
        self.assertIn("</head>", html)
        self.assertIn("<body>", html)
        self.assertIn("</body>", html)
        self.assertIn("katex.min.css", html)
        self.assertIn("katex.min.js", html)


class TestEditorTheme(unittest.TestCase):
    """Тесты переключения темы редактора."""

    def setUp(self):
        from markdown_editor_pkg.editor import MarkdownEditorPyQt
        self.editor = MarkdownEditorPyQt()

    def tearDown(self):
        self.editor.close()
        del self.editor

    def test_initial_editor_theme_is_light(self):
        """Тема редактора по умолчанию — light."""
        self.assertEqual(self.editor.theme_manager.editor_theme, "light")

    def test_set_editor_theme(self):
        """set_editor_theme корректно меняет editor_theme."""
        self.editor.theme_manager.set_editor_theme("dark", self.editor.editor)
        self.assertEqual(self.editor.theme_manager.editor_theme, "dark")

    def test_toggle_editor_theme_cycles_themes(self):
        """Переключение темы редактора работает по циклу."""
        self.editor.theme_manager.toggle_editor_theme()
        self.assertEqual(self.editor.theme_manager.editor_theme, "dark")
        self.editor.theme_manager.toggle_editor_theme()
        self.assertEqual(self.editor.theme_manager.editor_theme, "contrast")
        self.editor.theme_manager.toggle_editor_theme()
        self.assertEqual(self.editor.theme_manager.editor_theme, "light")


class TestCalloutProcessor(unittest.TestCase):
    """Тесты GitHub Callouts."""

    def test_callout_detection(self):
        """Callout-маркеры распознаются из blockquote."""
        from markdown_editor_pkg.callout_processor import CalloutProcessor
        cp = CalloutProcessor()

        html = '<blockquote><p>[!NOTE] Это заметка</p><p>Продолжение</p></blockquote>'
        result = cp.process(html)

        self.assertIn('class="callout callout-note"', result)
        self.assertIn("Это заметка", result)

    def test_normal_blockquote_unchanged(self):
        """Обычный blockquote без маркера не меняется."""
        from markdown_editor_pkg.callout_processor import CalloutProcessor
        cp = CalloutProcessor()

        html = '<blockquote><p>Просто цитата</p></blockquote>'
        result = cp.process(html)

        self.assertIn('<blockquote>', result)


class TestStrikethroughProcessor(unittest.TestCase):
    """Тесты зачёркивания."""

    def test_strikethrough(self):
        """~~text~~ заменяется на <del>text</del>."""
        from markdown_editor_pkg.latex_processor import StrikethroughProcessor
        sp = StrikethroughProcessor()

        html = "Это <b>~~зачёркнуто~~</b> текст"
        result = sp.apply(html)
        self.assertIn("<del>зачёркнуто</del>", result)

    def test_strikethrough_protects_code(self):
        """~~ внутри <code> и <pre> не меняется."""
        from markdown_editor_pkg.latex_processor import StrikethroughProcessor
        sp = StrikethroughProcessor()

        html = "<code>~~код~~</code> и ~~реальный~~"
        result = sp.apply(html)
        self.assertIn("<code>~~код~~</code>", result)
        self.assertIn("<del>реальный</del>", result)


class TestSessionManager(unittest.TestCase):
    """Тесты SessionManager."""

    def test_save_and_load(self):
        """Сохранение и загрузка сессии."""
        from markdown_editor_pkg.session_manager import SessionManager
        import tempfile
        from pathlib import Path

        test_path = "/tmp/test_session.md"
        SessionManager.save(test_path)
        loaded = SessionManager.load()
        self.assertEqual(loaded, test_path)


class TestThemesManager(unittest.TestCase):
    """Тесты ThemesManager."""

    def test_get_preview_css(self):
        from markdown_editor_pkg.themes import ThemesManager
        tm = ThemesManager()
        css = tm.get_preview_css()
        self.assertIn("background-color", css)

    def test_get_editor_style(self):
        from markdown_editor_pkg.themes import ThemesManager
        tm = ThemesManager()
        style = tm.get_editor_style()
        self.assertIn("QTextEdit", style)

    def test_theme_order(self):
        from markdown_editor_pkg.themes import ThemesManager
        tm = ThemesManager()
        self.assertEqual(tm.THEME_ORDER, ["light", "dark", "contrast"])


if __name__ == "__main__":
    unittest.main()
