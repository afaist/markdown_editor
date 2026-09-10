"""Help Handler — About dialog and Keyboard Shortcuts reference."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from markdown_editor_pkg import __version__
from markdown_editor_pkg.i18n import tr

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt

_GIGACODE_URL = "https://gigacode.ai"
_MARKDOWN_GUIDE_URL = "https://www.markdownguide.org"


class HelpHandler:
    """Help handler and About dialog."""

    def __init__(self, editor: MarkdownEditorPyQt):
        """Инициализация обработчика справки.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
        """
        self.editor = editor

    def show_about(self) -> None:
        """Показать диалог «О программе» с информацией и ссылкой на GigaCode."""
        dialog = QDialog(self.editor)
        dialog.setWindowTitle(tr("About"))
        dialog.setMinimumWidth(420)

        layout = QVBoxLayout(dialog)

        title = QLabel(tr("Markdown Editor (PyQt6)"))
        title.setFont(QFont("", 0, QFont.Weight.Bold))
        layout.addWidget(title)

        info = QLabel(
            tr("Version: {}").format(__version__)
            + "\n"
            + tr("Developed with Python 3.12+, PyQt6, QtWebEngine\nLaTeX and Markdown support.")
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        credits = QLabel(
            tr(
                'Author: A. Zinoviev (afaist)\nDevelopment assisted by <a href="{}">GigaCode</a>'
            ).format(_GIGACODE_URL)
        )
        credits.setWordWrap(True)
        credits.setTextFormat(Qt.TextFormat.RichText)
        credits.setOpenExternalLinks(True)
        layout.addWidget(credits)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec()

    def show_shortcuts(self) -> None:
        """Показать диалог со справкой по горячим клавишам.

        Отображает таблицу сочетаний клавиш для всех разделов меню.
        """
        dialog = QDialog(self.editor)
        dialog.setWindowTitle(tr("Keyboard Shortcuts"))
        dialog.setMinimumWidth(520)

        layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        sections: list[tuple[str, list[tuple[str, str]]]] = [
            (
                tr("File"),
                [
                    (tr("New"), "Ctrl+N"),
                    (tr("Open"), "Ctrl+O"),
                    (tr("Save"), "Ctrl+S"),
                    (tr("Close"), "Ctrl+W"),
                    (tr("Exit"), "Ctrl+Q"),
                ],
            ),
            (
                tr("Edit"),
                [
                    (tr("Undo"), "Ctrl+Z"),
                    (tr("Redo"), "Ctrl+Shift+Z"),
                    (tr("Cut"), "Ctrl+X"),
                    (tr("Copy"), "Ctrl+C"),
                    (tr("Paste"), "Ctrl+V"),
                    (tr("Find and Replace"), "Ctrl+F"),
                ],
            ),
            (
                tr("View"),
                [
                    (tr("Zoom In"), "Ctrl++"),
                    (tr("Zoom Out"), "Ctrl+-"),
                    (tr("Reset Zoom"), "Ctrl+0"),
                ],
            ),
            (
                tr("Styles"),
                [
                    (tr("Bold"), "Ctrl+B"),
                    (tr("Italic"), "Ctrl+I"),
                    (tr("Strikethrough"), "Ctrl+Shift+X"),
                    (tr("Inline Code"), "Ctrl+`"),
                ],
            ),
            (
                tr("Lists"),
                [
                    (tr("Bulleted List"), "Ctrl+Shift+U"),
                    (tr("Numbered List"), "Ctrl+Shift+O"),
                    (tr("Task List"), "Ctrl+Shift+T"),
                ],
            ),
            (
                tr("Headings"),
                [
                    (tr("Heading 1"), "Ctrl+Shift+1"),
                    (tr("Heading 2"), "Ctrl+Shift+2"),
                    (tr("Heading 3"), "Ctrl+Shift+3"),
                    (tr("Heading 4"), "Ctrl+Shift+4"),
                    (tr("Heading 5"), "Ctrl+Shift+5"),
                    (tr("Heading 6"), "Ctrl+Shift+6"),
                ],
            ),
            (
                tr("Blockquote"),
                [(tr("Quote"), "Ctrl+Shift+Q")],
            ),
            (
                tr("Callouts"),
                [
                    (tr("Note"), "Ctrl+Shift+7"),
                    (tr("Tip"), "Ctrl+Shift+8"),
                    (tr("Important"), "Ctrl+Shift+9"),
                    (tr("Warning"), "Ctrl+Shift+0"),
                    (tr("Caution"), "Ctrl+Shift+-"),
                ],
            ),
            (
                tr("Code Blocks"),
                [
                    ("Python", "Ctrl+Shift+C"),
                    ("Bash", "Ctrl+Shift+B"),
                    ("Markdown", "Ctrl+Shift+M"),
                    ("C++", "Ctrl+Shift+P"),
                    ("Rust", "Ctrl+Shift+R"),
                ],
            ),
            (
                tr("LaTeX"),
                [
                    (tr("Inline ($...$)"), "Ctrl+L"),
                    (tr("Block ($...$)"), "Ctrl+Shift+L"),
                    (tr("Fraction (\\frac)"), "Ctrl+Shift+F"),
                    (tr("Square Root (\\sqrt)"), "Ctrl+Shift+R"),
                    (tr("Superscript"), "Ctrl+Shift+S"),
                    (tr("Subscript"), "Ctrl+Shift+N"),
                    (tr("Sum (\\sum)"), "Ctrl+Shift+A"),
                    (tr("Integral (\\int)"), "Ctrl+Shift+G"),
                    (tr("Matrix (\\begin{matrix})"), "Ctrl+Shift+M"),
                ],
            ),
            (
                tr("Extras"),
                [
                    (tr("Horizontal Rule (---)"), "Ctrl+Shift+H"),
                    (tr("Table"), "Ctrl+Shift+Tab"),
                    (tr("HTML Comment"), "Ctrl+Shift+/"),
                ],
            ),
        ]

        for section_title, items in sections:
            section_label = QLabel(section_title)
            section_label.setFont(QFont("", 0, QFont.Weight.Bold))
            section_label.setStyleSheet("margin-top: 8px;")
            scroll_layout.addWidget(section_label)

            for action_name, shortcut in items:
                row = QLabel(f"{action_name}    {shortcut}")
                row.setStyleSheet("padding: 1px 0;")
                scroll_layout.addWidget(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec()

    def show_markdown_help(self) -> None:
        """Показать диалог-шпаргалку по синтаксису Markdown.

        Отображает примеры основных элементов синтаксиса и ссылку
        на подробное руководство на markdownguide.org.
        """
        dialog = QDialog(self.editor)
        dialog.setWindowTitle(tr("Markdown Help"))
        dialog.setMinimumWidth(560)
        # Dark background with white text for readability in any theme
        dialog.setStyleSheet(
            "QDialog { background-color: #2d2d2d; }"
            "QLabel { color: #f0f0f0; background-color: transparent; }"
            "QScrollArea { background-color: #2d2d2d; border: none; }"
        )

        layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        sections: list[tuple[str, list[str]]] = [
            (
                tr("Headings"),
                [
                    "# Heading 1",
                    "## Heading 2",
                    "### Heading 3",
                ],
            ),
            (
                tr("Emphasis"),
                [
                    "**Bold text**",
                    "*Italic text*",
                    "~~Strikethrough~~",
                    "`inline code`",
                ],
            ),
            (
                tr("Lists"),
                [
                    "- Unordered list item",
                    "1. Ordered list item",
                    "- [ ] Task list item",
                ],
            ),
            (
                tr("Links & Images"),
                [
                    "[Link text](https://example.com)",
                    "![Alt text](image.png)",
                ],
            ),
            (
                tr("Code Blocks"),
                [
                    "```python",
                    "code here",
                    "```",
                ],
            ),
            (
                tr("Blockquote"),
                [
                    "> Blockquoted text",
                ],
            ),
            (
                tr("LaTeX"),
                [
                    "Inline: $E = mc^2$",
                    "Block: $$\\sum_{i=1}^{n} x_i$$",
                ],
            ),
            (
                tr("Callouts"),
                [
                    "> [!NOTE]",
                    "> [!TIP]",
                    "> [!IMPORTANT]",
                    "> [!WARNING]",
                    "> [!CAUTION]",
                ],
            ),
            (
                tr("Horizontal Rule"),
                [
                    "---",
                ],
            ),
        ]

        for section_title, items in sections:
            section_label = QLabel(section_title)
            section_label.setFont(QFont("", 0, QFont.Weight.Bold))
            section_label.setStyleSheet(
                "margin-top: 8px; color: #f0f0f0; background-color: transparent;"
            )
            scroll_layout.addWidget(section_label)

            for item in items:
                code_label = QLabel(item)
                code_label.setStyleSheet(
                    "background-color: #3c3c3c; color: #f0f0f0; padding: 2px 6px; "
                    "border-radius: 3px; font-family: Consolas, monospace;"
                )
                scroll_layout.addWidget(code_label)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        link_label = QLabel(
            tr('For a detailed Markdown guide, visit: <a href="{}">markdownguide.org</a>').format(
                _MARKDOWN_GUIDE_URL
            )
        )
        link_label.setWordWrap(True)
        link_label.setTextFormat(Qt.TextFormat.RichText)
        link_label.setOpenExternalLinks(True)
        layout.addWidget(link_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec()
