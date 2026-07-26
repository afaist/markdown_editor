# Markdown Editor - Тесты

"""
Тесты для Markdown Editor
"""

import unittest
import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestMarkdownRenderer(unittest.TestCase):
    """Тесты рендеринга Markdown"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Импортируем после добавления пути
        from markdown_editor import MarkdownEditor
        import tkinter as tk
        
        self.root = tk.Tk()
        self.editor = MarkdownEditor(self.root)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.root.destroy()
    
    def test_simple_text(self):
        """Тест простого текста"""
        text = "Простой текст"
        html = self.editor.render_markdown(text)
        self.assertIn("<p>Простой текст</p>", html)
    
    def test_headings(self):
        """Тест заголовков"""
        text = "# Заголовок 1\n## Заголовок 2\n### Заголовок 3"
        html = self.editor.render_markdown(text)
        self.assertIn("<h1", html)
        self.assertIn("Заголовок 1", html)
        self.assertIn("<h2", html)
        self.assertIn("Заголовок 2", html)
        self.assertIn("<h3", html)
        self.assertIn("Заголовок 3", html)
    
    def test_bold_italic(self):
        """Тест жирного и курсива"""
        text = "**жирный** и *курсив*"
        html = self.editor.render_markdown(text)
        self.assertIn("<strong>жирный</strong>", html)
        self.assertIn("<em>курсив</em>", html)
    
    def test_lists(self):
        """Тест списков"""
        text = "- Элемент 1\n- Элемент 2\n1. Пункт 1\n2. Пункт 2"
        html = self.editor.render_markdown(text)
        self.assertIn("<ul>", html)
        self.assertIn("<li>Элемент 1</li>", html)
        self.assertIn("<ol>", html)
    
    def test_links(self):
        """Тест ссылок"""
        text = "[Текст ссылки](https://example.com)"
        html = self.editor.render_markdown(text)
        self.assertIn('href="https://example.com"', html)
        self.assertIn("Текст ссылки", html)
    
    def test_images(self):
        """Тест изображений"""
        text = "![Альтернативный текст](image.png)"
        html = self.editor.render_markdown(text)
        self.assertIn('alt="Альтернативный текст"', html)
        self.assertIn('src="image.png"', html)
    
    def test_code(self):
        """Тест кода"""
        text = "```\nкод\n```"
        html = self.editor.render_markdown(text)
        self.assertIn("<pre", html)
        self.assertIn("<code>", html)
        self.assertIn("код", html)
    
    def test_blockquotes(self):
        """Тест цитат"""
        text = "> Это цитата"
        html = self.editor.render_markdown(text)
        self.assertIn("<blockquote>", html)
    
    def test_latex_inline(self):
        """Тест встроенных LaTeX-формул"""
        text = "Формула: $a^2 + b^2 = c^2$"
        html = self.editor.render_markdown(text)
        self.assertIn("Формула:", html)
        self.assertIn("a<sup>2</sup>", html)
        self.assertIn("b<sup>2</sup>", html)
        self.assertIn("c<sup>2</sup>", html)
        # Проверяем класс MathJax
        self.assertIn('class="math-tex"', html)
    
    def test_latex_block(self):
        """Тест блочных LaTeX-формул"""
        text = "$$\\int_0^1 x^2 dx$$"
        html = self.editor.render_markdown(text)
        # Проверяем класс MathJax для блочных формул
        self.assertIn('class="math-tex"', html)
        self.assertIn("\\int_0^1", html)
    
    def test_tables(self):
        """Тест таблиц"""
        text = "| Заголовок 1 | Заголовок 2 |\n|-------------|-------------|\n| Ячейка 1 | Ячейка 2 |"
        html = self.editor.render_markdown(text)
        self.assertIn("<table>", html)
        self.assertIn("<th>", html)
        self.assertIn("<td>", html)
    
    def test_complex_document(self):
        """Тест сложного документа"""
        text = """
# Заголовок

Это **жирный** текст и *курсив*.

## Список

- Элемент 1
- Элемент 2

## Формула

Формула: $E = mc^2$

## Код

```
def hello():
    print("Hello")
```
"""
        html = self.editor.render_markdown(text)
        self.assertIn("<h1", html)
        self.assertIn("Заголовок", html)
        self.assertIn("<strong>жирный</strong>", html)
        self.assertIn("<ul>", html)
        self.assertIn("Список", html)


class TestLatexProcessing(unittest.TestCase):
    """Тесты обработки LaTeX-формул"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        from markdown_editor import MarkdownEditor
        import tkinter as tk
        
        self.root = tk.Tk()
        self.editor = MarkdownEditor(self.root)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.root.destroy()
    
    def test_inline_latex_conversion(self):
        """Тест конвертации встроенных формул"""
        html = self.editor.process_latex("Текст $a + b$ текст")
        self.assertIn('<span class="math-tex">', html)
        self.assertIn("a + b", html)
    
    def test_block_latex_conversion(self):
        """Тест конвертации блочных формул"""
        html = self.editor.process_latex("Текст $$\\int x dx$$ текст")
        self.assertIn('<div class="math-tex">', html)
        self.assertIn("\\int x dx", html)
    
    def test_multiple_formulas(self):
        """Тест нескольких формул"""
        html = self.editor.process_latex("$a$ и $b$ и $$c$$")
        self.assertIn('<span class="math-tex">a</span>', html)
        self.assertIn('<span class="math-tex">b</span>', html)
        self.assertIn('<div class="math-tex">c</div>', html)


class TestThemeSwitching(unittest.TestCase):
    """Тесты переключения тем"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        from markdown_editor import MarkdownEditor
        import tkinter as tk
        
        self.root = tk.Tk()
        self.editor = MarkdownEditor(self.root)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.root.destroy()
    
    def test_theme_toggle(self):
        """Тест переключения темы"""
        initial_theme = self.editor.current_theme
        self.editor.toggle_theme()
        self.assertNotEqual(initial_theme, self.editor.current_theme)
    
    def test_theme_apply(self):
        """Тест применения темы"""
        self.editor.apply_theme()
        self.assertIn(self.editor.current_theme, ["light", "dark"])


if __name__ == "__main__":
    unittest.main()
