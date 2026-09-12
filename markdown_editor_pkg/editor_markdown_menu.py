"""Markdown меню MarkdownEditorPyQt.

Содержит:
- setup_markdown_menu — создание меню Markdown с подпунктами форматирования
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow, QMenu

from markdown_editor_pkg.i18n import tr

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class MarkdownMenuBuilder:
    """Creates Markdown menu with formatting submenus."""

    def __init__(self, editor: MarkdownEditorPyQt) -> None:
        self._editor = editor

    def build(self) -> None:
        """Assemble the Markdown menu and add it to the menubar."""
        parent = self._editor
        menubar = parent.menuBar()
        if menubar is None:
            return

        md_menu = menubar.addMenu(tr("Markdown"))
        if md_menu is None:
            return

        self._build_headings(md_menu, parent)
        self._build_styles(md_menu, parent)
        self._build_lists(md_menu, parent)
        self._build_blockquote(md_menu, parent)
        self._build_callouts(md_menu, parent)
        self._build_code(md_menu, parent)
        self._build_latex(md_menu, parent)
        self._build_extra(md_menu, parent)

    def _build_headings(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Create Headings submenu."""
        headings_menu = md_menu.addMenu(tr("Headings"))
        if headings_menu is None:
            return
        heading_labels: list[str] = [
            tr("Heading 1"),
            tr("Heading 2"),
            tr("Heading 3"),
            tr("Heading 4"),
            tr("Heading 5"),
            tr("Heading 6"),
        ]
        for i, label in enumerate(heading_labels, start=1):
            action = QAction(label, parent)
            action.setShortcut(QKeySequence(f"Ctrl+Shift+{i}"))
            action.triggered.connect(
                lambda checked, level=i: parent.text_insertions.insert_heading(level)  # type: ignore[attr-defined]
            )
            headings_menu.addAction(action)

    def _build_styles(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Create Styles submenu."""
        styles_menu = md_menu.addMenu(tr("Styles"))
        if styles_menu is None:
            return

        self._add_action(
            styles_menu,
            tr("Bold"),
            parent.text_insertions.insert_bold,  # type: ignore[attr-defined]
            "Ctrl+B",
        )
        self._add_action(
            styles_menu,
            tr("Italic"),
            parent.text_insertions.insert_italic,  # type: ignore[attr-defined]
            "Ctrl+I",
        )
        self._add_action(
            styles_menu,
            tr("Strikethrough"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_strikethrough,  # type: ignore[attr-defined]
            "Ctrl+Shift+X",
        )
        self._add_action(
            styles_menu,
            tr("Inline Code"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_inline_code,  # type: ignore[attr-defined]
            "Ctrl+`",
        )  # type: ignore[attr-defined]

    def _build_lists(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Create Lists submenu."""
        lists_menu = md_menu.addMenu(tr("Lists"))
        if lists_menu is None:
            return

        self._add_action(
            lists_menu,
            tr("Bulleted"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_unordered_list,  # type: ignore[attr-defined]
            "Ctrl+Shift+U",
        )
        self._add_action(
            lists_menu,
            tr("Numbered"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_ordered_list,  # type: ignore[attr-defined]
            "Ctrl+Shift+O",
        )
        self._add_action(
            lists_menu,
            tr("Task List"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_task_list,  # type: ignore[attr-defined]
            "Ctrl+Shift+T",
        )

    def _build_blockquote(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Add Quote menu item."""
        bq_action = QAction(tr("Quote"), parent)
        bq_action.setShortcut(QKeySequence("Ctrl+Shift+Q"))
        bq_action.triggered.connect(parent.text_insertions.insert_blockquote)  # type: ignore[attr-defined]
        md_menu.addAction(bq_action)

    def _build_callouts(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Create Callouts submenu."""
        callouts_menu = md_menu.addMenu(tr("Callouts"))
        if callouts_menu is None:
            return

        for callout_type, label, shortcut in [
            ("NOTE", tr("Note"), "Ctrl+Shift+7"),
            ("TIP", tr("Tip"), "Ctrl+Shift+8"),
            ("IMPORTANT", tr("Important"), "Ctrl+Shift+9"),
            ("WARNING", tr("Warning"), "Ctrl+Shift+0"),
            ("CAUTION", tr("Caution"), "Ctrl+Shift+-"),
        ]:
            action = QAction(label, parent)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(
                lambda checked, ct=callout_type: parent.text_insertions.insert_callout(ct)  # type: ignore[attr-defined]
            )
            callouts_menu.addAction(action)

    def _build_code(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Create Code submenu."""
        code_menu = md_menu.addMenu(tr("Code"))
        if code_menu is None:
            return

        for lang, label, shortcut in [
            ("python", "Python", "Ctrl+Shift+C"),
            ("bash", "Bash", "Ctrl+Shift+B"),
            ("markdown", "Markdown", "Ctrl+Shift+M"),
            ("cpp", "C++", "Ctrl+Shift+P"),
            ("rust", "Rust", "Ctrl+Shift+R"),
        ]:
            a = QAction(label, parent)
            a.setShortcut(QKeySequence(shortcut))
            a.triggered.connect(
                lambda checked, lang=lang: parent.text_insertions.insert_code_block(lang)  # type: ignore[attr-defined]
            )
            code_menu.addAction(a)

    def _build_latex(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Create LaTeX submenu."""
        latex_menu = md_menu.addMenu(tr("LaTeX"))
        if latex_menu is None:
            return

        self._add_action(
            latex_menu,
            tr("Inline ($...$)"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_inline_latex,  # type: ignore[attr-defined]
            "Ctrl+L",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            tr("Block ($...$)"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_block_latex,  # type: ignore[attr-defined]
            "Ctrl+Shift+L",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            tr("Fraction (\\frac)"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_fraction,  # type: ignore[attr-defined]
            "Ctrl+Shift+F",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            tr("Square Root (\\sqrt)"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_sqrt,  # type: ignore[attr-defined]
            "Ctrl+Shift+R",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            tr("Superscript"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_superscript,  # type: ignore[attr-defined]
            "Ctrl+Shift+S",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            tr("Subscript"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_subscript,  # type: ignore[attr-defined]
            "Ctrl+Shift+N",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            tr("Sum (\\sum)"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_sum,  # type: ignore[attr-defined]
            "Ctrl+Shift+A",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            tr("Integral (\\int)"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_integral,  # type: ignore[attr-defined]
            "Ctrl+Shift+G",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            tr("Matrix (\\begin{matrix})"),  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_matrix,  # type: ignore[attr-defined]
            "Ctrl+Shift+M",
        )  # type: ignore[attr-defined]

    def _build_extra(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Add extra menu items."""
        hr_action = QAction(tr("Horizontal Rule (---)"), parent)
        hr_action.setShortcut(QKeySequence("Ctrl+Shift+H"))
        hr_action.triggered.connect(parent.text_insertions.insert_horizontal_rule)  # type: ignore[attr-defined]
        md_menu.addAction(hr_action)

        table_action = QAction(tr("Table"), parent)
        table_action.setShortcut(QKeySequence("Ctrl+Shift+Tab"))
        table_action.triggered.connect(parent.text_insertions.insert_table)  # type: ignore[attr-defined]
        md_menu.addAction(table_action)

        comment_action = QAction(tr("HTML Comment"), parent)
        comment_action.setShortcut(QKeySequence("Ctrl+Shift+/"))
        comment_action.triggered.connect(parent.text_insertions.insert_html_comment)  # type: ignore[attr-defined]
        md_menu.addAction(comment_action)

        emoji_action = QAction(tr("Emoji"), parent)
        emoji_action.setShortcut(QKeySequence("Ctrl+E"))
        emoji_action.triggered.connect(parent._show_emoji_picker)  # type: ignore[attr-defined]
        md_menu.addAction(emoji_action)

    @staticmethod
    def _add_action(
        menu: QMenu,
        text: str,
        callback: Callable[[], None],  # type: ignore[type-arg]
        shortcut: str | QKeySequence | QKeySequence.StandardKey | None = None,
    ) -> None:
        """Add a QAction to the menu."""
        action = QAction(text, menu)
        if shortcut is not None:
            if isinstance(shortcut, str):
                action.setShortcut(QKeySequence(shortcut))
            else:
                action.setShortcut(shortcut)
        action.triggered.connect(callback)
        menu.addAction(action)
