#!/usr/bin/env python3
"""Test runner for markdown_editor module - unit tests without GUI"""

import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment BEFORE importing anything else
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Import QtWebEngineWidgets first
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)

from markdown_editor import MarkdownEditorPyQt
import markdown

# Test simple rendering
md = "Простой текст"
editor = MarkdownEditorPyQt()
editor.setWindowTitle("Test")
html = editor.render_markdown(md)
print("Simple render:", "PASS" if "<p>Простой текст</p>" in html else "FAIL")

# Test headings
md = "# Заголовок 1\n## Заголовок 2\n### Заголовок 3"
html = editor.render_markdown(md)
print("Headings:", "PASS" if "<h1>Заголовок 1</h1>" in html and "<h2>Заголовок 2</h2>" in html and "<h3>Заголовок 3</h3>" in html else "FAIL")

# Test inline latex
md = "Формула: $a^2 + b^2 = c^2$"
html = editor.render_markdown(md)
print("Inline latex:", "PASS" if "a<sup>2</sup>" in html and "b<sup>2</sup>" in html and "c<sup>2</sup>" in html else "FAIL")

# Test block latex
md = "$$\\int_0^1 x^2 dx$$"
html = editor.render_markdown(md)
print("Block latex:", "PASS" if "\\int_0^1" in html else "FAIL")

# Test full HTML structure
md = "# Привет"
html = editor.render_markdown(md)
print("Full HTML:", "PASS" if html.startswith("<!DOCTYPE html>") and "<html>" in html and "</html>" in html else "FAIL")

# Test themes
print("Themes:", "PASS" if "light" in editor.themes and "dark" in editor.themes and "contrast" in editor.themes else "FAIL")

# Test editor_theme
print("Editor theme:", "PASS" if editor.editor_theme == "light" else "FAIL")

editor.close()

print("\nAll tests completed!")
