"""Markdown меню MarkdownEditorPyQt.

Содержит:
- setup_markdown_menu — создание меню Markdown с подпунктами форматирования
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow, QMenu

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class MarkdownMenuBuilder:
    """Создаёт меню Markdown с подпунктами."""

    def __init__(self, editor: MarkdownEditorPyQt) -> None:
        self._editor = editor

    def build(self) -> None:
        """Собрать меню Markdown и добавить его в menubar."""
        parent = self._editor
        menubar = parent.menuBar()
        if menubar is None:
            return

        md_menu = menubar.addMenu("Markdown")
        if md_menu is None:
            return

        self._build_headings(md_menu, parent)
        self._build_styles(md_menu, parent)
        self._build_lists(md_menu, parent)
        self._build_blockquote(md_menu, parent)
        self._build_code(md_menu, parent)
        self._build_latex(md_menu, parent)
        self._build_extra(md_menu, parent)

    def _build_headings(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Создать подменю Заголовки."""
        headings_menu = md_menu.addMenu("Заголовки")
        if headings_menu is None:
            return
        for i in range(1, 8):
            action = QAction(f"Заголовок {i}", parent)
            action.setShortcut(QKeySequence(f"Ctrl+Shift+{i}"))
            action.triggered.connect(
                lambda checked, level=i: parent.text_insertions.insert_heading(level)  # type: ignore[attr-defined]
            )
            headings_menu.addAction(action)

    def _build_styles(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Создать подменю Стили."""
        styles_menu = md_menu.addMenu("Стили")
        if styles_menu is None:
            return

        self._add_action(
            styles_menu,
            "Жирный",
            parent.text_insertions.insert_bold,  # type: ignore[attr-defined]
            "Ctrl+B",
        )
        self._add_action(
            styles_menu,
            "Курсив",
            parent.text_insertions.insert_italic,  # type: ignore[attr-defined]
            "Ctrl+I",
        )
        self._add_action(
            styles_menu,
            "Зачёркнутый",  # type: ignore[attr-defined]
            parent.text_insertions.insert_strikethrough,  # type: ignore[attr-defined]
            "Ctrl+Shift+X",
        )
        self._add_action(
            styles_menu,
            "Встроенный код",  # type: ignore[attr-defined]
            parent.text_insertions.insert_inline_code,  # type: ignore[attr-defined]
            "Ctrl+`",
        )  # type: ignore[attr-defined]

    def _build_lists(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Создать подменю Списки."""
        lists_menu = md_menu.addMenu("Списки")
        if lists_menu is None:
            return

        self._add_action(
            lists_menu,
            "Маркированный",  # type: ignore[attr-defined]
            parent.text_insertions.insert_unordered_list,  # type: ignore[attr-defined]
            "Ctrl+Shift+U",
        )
        self._add_action(
            lists_menu,
            "Нумерованный",  # type: ignore[attr-defined]
            parent.text_insertions.insert_ordered_list,  # type: ignore[attr-defined]
            "Ctrl+Shift+O",
        )
        self._add_action(
            lists_menu,
            "Список задач",  # type: ignore[attr-defined]
            parent.text_insertions.insert_task_list,  # type: ignore[attr-defined]
            "Ctrl+Shift+T",
        )

    def _build_blockquote(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Добавить пункт Цитата."""
        bq_action = QAction("Цитата", parent)
        bq_action.setShortcut(QKeySequence("Ctrl+Shift+Q"))
        bq_action.triggered.connect(parent.text_insertions.insert_blockquote)  # type: ignore[attr-defined]
        md_menu.addAction(bq_action)

    def _build_code(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Создать подменю Код."""
        code_menu = md_menu.addMenu("Код")
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
        """Создать подменю LaTeX."""
        latex_menu = md_menu.addMenu("LaTeX")
        if latex_menu is None:
            return

        self._add_action(
            latex_menu,
            "Встроенная ($...$)",  # type: ignore[attr-defined]
            parent.text_insertions.insert_inline_latex,  # type: ignore[attr-defined]
            "Ctrl+L",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            "Блочная ($...$)",  # type: ignore[attr-defined]
            parent.text_insertions.insert_block_latex,  # type: ignore[attr-defined]
            "Ctrl+Shift+L",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            "Дробь (\\frac)",  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_fraction,  # type: ignore[attr-defined]
            "Ctrl+Shift+F",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            "Квадратный корень (\\sqrt)",  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_sqrt,  # type: ignore[attr-defined]
            "Ctrl+Shift+R",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            "Надстрочный",  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_superscript,  # type: ignore[attr-defined]
            "Ctrl+Shift+S",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            "Подстрочный",  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_subscript,  # type: ignore[attr-defined]
            "Ctrl+Shift+N",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            "Сумма (\\sum)",  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_sum,  # type: ignore[attr-defined]
            "Ctrl+Shift+A",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            "Интеграл (\\int)",  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_integral,  # type: ignore[attr-defined]
            "Ctrl+Shift+G",
        )  # type: ignore[attr-defined]
        self._add_action(
            latex_menu,
            "Матрица (\\begin{matrix})",  # type: ignore[attr-defined]
            parent.text_insertions.insert_latex_matrix,  # type: ignore[attr-defined]
            "Ctrl+Shift+M",
        )  # type: ignore[attr-defined]

    def _build_extra(self, md_menu: QMenu, parent: QMainWindow) -> None:
        """Добавить дополнительные пункты."""
        hr_action = QAction("Разделитель (---)", parent)
        hr_action.setShortcut(QKeySequence("Ctrl+Shift+H"))
        hr_action.triggered.connect(parent.text_insertions.insert_horizontal_rule)  # type: ignore[attr-defined]
        md_menu.addAction(hr_action)

        table_action = QAction("Таблица", parent)
        table_action.setShortcut(QKeySequence("Ctrl+Shift+Tab"))
        table_action.triggered.connect(parent.text_insertions.insert_table)  # type: ignore[attr-defined]
        md_menu.addAction(table_action)

        comment_action = QAction("HTML-комментарий", parent)
        comment_action.setShortcut(QKeySequence("Ctrl+Shift+/"))
        comment_action.triggered.connect(parent.text_insertions.insert_html_comment)  # type: ignore[attr-defined]
        md_menu.addAction(comment_action)

    @staticmethod
    def _add_action(
        menu: QMenu,
        text: str,
        callback: Callable[[], None],  # type: ignore[type-arg]
        shortcut: str = "",
    ) -> None:
        """Добавить QAction в меню."""
        action = QAction(text, menu)  # Используем menu как parent для QAction, если это QMenu
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        menu.addAction(action)
