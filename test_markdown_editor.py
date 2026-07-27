# test_markdown_editor.py
# Updated Markdown Editor Tests (PyQt6-based)

import unittest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import QtWebEngineWidgets first to satisfy Qt requirements
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication

# Get the QApplication instance from conftest
app = QApplication.instance()


class TestLatexProcessing(unittest.TestCase):
    """Тесты обработки LaTeX-формул через process_latex_before_markdown"""

    def setUp(self):
        from markdown_editor import MarkdownEditorPyQt
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")
        # Очищаем кэш перед каждым тестом, чтобы индексы были предсказуемыми
        self.editor.display_math_cache = []
        self.editor.inline_math_cache = []

    def tearDown(self):
        self.editor.close()
        del self.editor

    def test_inline_latex_preserved(self):
        """Тест: встроенные формулы $...$ должны быть заменены на плейсхолдеры"""
        text = "Формула: $a^2 + b^2 = c^2$"
        processed = self.editor.process_latex_before_markdown(text)

        # Проверяем, что формула заменена на плейсхолдер и сохранена в кэше
        self.assertIn("<!-- inline-math-0 -->", processed)
        self.assertIn("a^2 + b^2 = c^2", self.editor.inline_math_cache)

    def test_block_latex_preserved(self):
        """Тест: блочные формулы $$...$$ должны быть заменены на плейсхолдеры"""
        text = "$$\\int_0^1 x^2 dx$$"
        processed = self.editor.process_latex_before_markdown(text)

        self.assertIn("<!-- display-math-0 -->", processed)
        self.assertIn("\\int_0^1 x^2 dx", self.editor.display_math_cache)

    def test_multiple_formulas(self):
        """Тест: несколько формул одного и другого типа"""
        text = "$a$ и $b$ и $$c$$"
        processed = self.editor.process_latex_before_markdown(text)

        self.assertIn("<!-- inline-math-0 -->", processed)
        self.assertIn("<!-- inline-math-1 -->", processed)
        self.assertIn("<!-- display-math-0 -->", processed)

        self.assertEqual(len(self.editor.inline_math_cache), 2)
        self.assertEqual(len(self.editor.display_math_cache), 1)
        self.assertIn("a", self.editor.inline_math_cache[0])
        self.assertIn("b", self.editor.inline_math_cache[1])
        self.assertIn("c", self.editor.display_math_cache[0])

    def test_latex_with_nested_sup_sub(self):
        """Тест: корректное извлечение формул со степенями и индексами"""
        text = "$E = mc^2$ и $x_1 + x_2$"
        processed = self.editor.process_latex_before_markdown(text)
        self.assertIn("E = mc^2", self.editor.inline_math_cache[0])
        self.assertIn("x_1 + x_2", self.editor.inline_math_cache[1])


class TestThemeSwitching(unittest.TestCase):
    """Тесты переключения тем (проверка внутренних атрибутов)"""

    def setUp(self):
        from markdown_editor import MarkdownEditorPyQt
        self.editor = MarkdownEditorPyQt()

    def tearDown(self):
        self.editor.close()
        del self.editor

    def test_initial_theme_is_light(self):
        """По умолчанию тема предпросмотра — light"""
        self.assertEqual(self.editor.theme_name, "light")

    def test_theme_toggle(self):
        """Переключение темы корректно обновляет theme_name"""
        initial = self.editor.theme_name
        self.editor.toggle_theme()
        self.assertNotEqual(initial, self.editor.theme_name)

        # Проверяем полный цикл: light → dark → contrast → light
        self.editor.toggle_theme()
        self.editor.toggle_theme()
        self.assertEqual(self.editor.theme_name, "light")

    def test_set_theme(self):
        """Метод set_theme устанавливает нужную тему"""
        self.editor.set_theme("dark")
        self.assertEqual(self.editor.theme_name, "dark")
        self.editor.set_theme("contrast")
        self.assertEqual(self.editor.theme_name, "contrast")

    def test_themes_dict_exists(self):
        """Словарь themes содержит все необходимые темы"""
        self.assertIn("light", self.editor.themes)
        self.assertIn("dark", self.editor.themes)
        self.assertIn("contrast", self.editor.themes)
        for theme_name, css in self.editor.themes.items():
            self.assertIsInstance(css, str)
            self.assertGreater(len(css), 0)


class TestMarkdownRender(unittest.TestCase):
    """Полный тест рендеринга Markdown в HTML (с поддержкой LaTeX)"""

    def setUp(self):
        from markdown_editor import MarkdownEditorPyQt
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def tearDown(self):
        self.editor.close()
        del self.editor

    def test_simple_render(self):
        """Тест: простой Markdown рендерится в правильный HTML"""
        md = "Простой текст"
        html = self.editor.render_markdown(md)
        self.assertIn("<p>Простой текст</p>", html)

    def test_headings_render(self):
        """Тест: заголовки H1–H3 рендерятся"""
        md = "# Заголовок 1\n## Заголовок 2\n### Заголовок 3"
        html = self.editor.render_markdown(md)
        for i in range(1, 4):
            # Заголовки имеют id атрибуты от markdown.extensions.toc
            self.assertIn(f"<h{i} id=\"{i}\">Заголовок {i}</h{i}>", html)

    def test_latex_inline_render(self):
        """Тест: встроенные формулы $...$ корректно обрабатываются
        
        Формулы не рендерятся в HTML напрямую - они передаются на рендеринг
        KaTeX в браузере через JavaScript. Проверяем наличие исходных формул
        и скриптов KaTeX.
        """
        md = "Формула: $a^2 + b^2 = c^2$"
        html = self.editor.render_markdown(md)
        # Проверяем наличие исходной формулы
        self.assertIn("$a^2 + b^2 = c^2$", html)
        # Проверяем наличие скриптов KaTeX
        self.assertIn("katex.min.js", html)
        self.assertIn("auto-render.min.js", html)
        # Проверяем наличие delimiters для встроенных формул
        self.assertIn('{left: "$", right: "$", display: false}', html)

    def test_latex_block_render(self):
        """Тест: блочные формулы $$...$$ корректно обрабатываются
        
        Формулы не рендерятся в HTML напрямую - они передаются на рендеринг
        KaTeX в браузере через JavaScript. Проверяем наличие исходных формул
        и скриптов KaTeX.
        """
        md = "$$\\int_0^1 x^2 dx$$"
        html = self.editor.render_markdown(md)
        # Проверяем наличие исходной формулы
        self.assertIn("$$\\int_0^1 x^2 dx$$", html)
        # Проверяем наличие скриптов KaTeX
        self.assertIn("katex.min.js", html)
        self.assertIn("auto-render.min.js", html)
        # Проверяем наличие delimiters для блочных формул
        self.assertIn('{left: "$$", right: "$$", display: true}', html)

    def test_full_html_structure(self):
        """Тест: рендеринг возвращает полный HTML-документ"""
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
    """Тесты переключения темы редактора (editor_theme)"""

    def setUp(self):
        from markdown_editor import MarkdownEditorPyQt
        self.editor = MarkdownEditorPyQt()

    def tearDown(self):
        self.editor.close()
        del self.editor

    def test_initial_editor_theme_is_light(self):
        """Тема редактора по умолчанию — light"""
        self.assertEqual(self.editor.editor_theme, "light")

    def test_set_editor_theme(self):
        """Метод set_editor_theme корректно меняет editor_theme"""
        self.editor.set_editor_theme("dark")
        self.assertEqual(self.editor.editor_theme, "dark")

    def test_toggle_editor_theme_cycles_themes(self):
        """Переключение темы редактора работает по циклу"""
        self.editor.toggle_editor_theme()  # light → dark
        self.assertEqual(self.editor.editor_theme, "dark")
        self.editor.toggle_editor_theme()  # dark → contrast
        self.assertEqual(self.editor.editor_theme, "contrast")
        self.editor.toggle_editor_theme()  # contrast → light
        self.assertEqual(self.editor.editor_theme, "light")


if __name__ == "__main__":
    unittest.main()
