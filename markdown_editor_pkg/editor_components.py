"""UI комбинаторы для MarkdownEditorPyQt — сборка интерфейса из компонентов.

Содержит:
- UIBuilder — создание основного UI (сплиттер, редактор, превью, статусбар)
- ToolbarBuilder — создание панели инструментов
- MenuBuilder — создание меню (File, Edit, View, Help)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QFont, QAction, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QSplitter,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QToolBar,
    QStatusBar,
    QLabel,
    QComboBox,
    QPushButton,
    QMenuBar,
    QMenu,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from markdown_editor_pkg.editor_keypress import MarkdownTextEdit

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class UIBuilder:
    """Создаёт основной UI: сплиттер, редактор, предпросмотр, статусбар."""

    def __init__(self, editor: MarkdownEditorPyQt) -> None:
        self._editor = editor

    def build(self, parent: QMainWindow | None = None) -> None:
        """Собрать весь UI и добавить его в parent (MarkdownEditorPyQt)."""
        p = parent or self._editor
        self._build_splitter(p)
        self._build_statusbar(p)
        self._connect_signals(p)

    def _build_splitter(self, parent: QMainWindow) -> None:
        """Создать QSplitter с редактором и предпросмотром."""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        parent.setCentralWidget(splitter)

        # -- Редактор --
        editor_frame = QFrame()
        editor_layout = QVBoxLayout()
        editor_layout.setSpacing(0)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_frame.setLayout(editor_layout)

        editor_label = QLabel("Редактор Markdown")
        editor_label.setStyleSheet("background-color: #f0f0f0; color: #333333;")
        editor_label.setMinimumHeight(25)
        editor_label.setMaximumHeight(25)
        editor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor_layout.addWidget(editor_label)

        text_edit = MarkdownTextEdit()
        text_edit.setFont(QFont("Consolas", 11))
        self._editor.theme_manager.set_editor_theme("light", text_edit)
        editor_layout.addWidget(text_edit)
        self._editor.editor = text_edit  # type: ignore[attr-defined]

        splitter.addWidget(editor_frame)

        # -- Предпросмотр --
        preview_frame = QFrame()
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(0)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_frame.setLayout(preview_layout)

        preview_label = QLabel("Предпросмотр")
        preview_label.setStyleSheet("background-color: #f0f0f0; color: #333333;")
        preview_label.setMinimumHeight(25)
        preview_label.setMaximumHeight(25)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_label)

        preview = QWebEngineView()
        preview_layout.addWidget(preview)
        self._editor.preview = preview  # type: ignore[attr-defined]

        splitter.addWidget(preview_frame)
        splitter.setSizes([600, 600])

    def _build_statusbar(self, parent: QMainWindow) -> None:
        """Создать строку состояния с метками."""
        statusbar = QStatusBar()
        parent.setStatusBar(statusbar)
        self._editor._statusbar_ref = statusbar  # type: ignore[attr-defined]

        char_count_label = QLabel("Символов: 0")
        word_count_label = QLabel("Слов: 0")
        file_name_label = QLabel("")
        file_name_label.setMinimumWidth(250)

        statusbar.addPermanentWidget(file_name_label)
        statusbar.addPermanentWidget(char_count_label)
        statusbar.addPermanentWidget(word_count_label)

        self._editor.file_name_label = file_name_label  # type: ignore[attr-defined]
        self._editor.char_count_label = char_count_label  # type: ignore[attr-defined]
        self._editor.word_count_label = word_count_label  # type: ignore[attr-defined]

    def _connect_signals(self, parent: QMainWindow) -> None:
        """Подключить сигналы editor.textChanged."""
        parent.editor.textChanged.connect(parent.on_text_change)  # type: ignore[attr-defined]
        parent.editor.textChanged.connect(parent.update_char_count)  # type: ignore[attr-defined]
        parent.editor.textChanged.connect(parent.update_file_status)  # type: ignore[attr-defined]


class ToolbarBuilder:
    """Создаёт панель инструментов (QToolBar) с кнопками форматирования."""

    def __init__(self, editor: MarkdownEditorPyQt) -> None:
        self._editor = editor

    def build(self) -> None:
        """Собрать тулбар и добавить его в editor."""

        style_sheet_lbl = "color: white;"

        parent = self._editor
        toolbar = QToolBar("Форматирование")
        parent.addToolBar(toolbar)

        lbl_headers = QLabel("Заголовки: ")
        lbl_headers.setStyleSheet(style_sheet_lbl)
        lbl_headers.adjustSize()
        toolbar.addWidget(lbl_headers)

        # -- Выбор уровня заголовка --
        heading_combo = QComboBox()
        for lvl in range(1, 7):
            heading_combo.addItem(f"H{lvl}")
        heading_combo.setCurrentIndex(0)
        heading_combo.setToolTip("Уровень заголовка (1–6)")
        heading_combo.activated.connect(self._on_heading_combo_activated)  # type: ignore[attr-defined]

        heading_combo.setMinimumWidth(80)
        toolbar.addWidget(heading_combo)
        parent.heading_combo = heading_combo  # type: ignore[attr-defined]
        toolbar.addSeparator()

        lbl_formating = QLabel("Стили: ")
        lbl_formating.setStyleSheet(style_sheet_lbl)
        lbl_formating.adjustSize()
        toolbar.addWidget(lbl_formating)

        # -- Форматирование --
        actions: list[tuple[str, Callable[[], None]]] = [
            ("Жирный", parent.text_insertions.insert_bold),  # type: ignore[attr-defined]
            ("Курсив", parent.text_insertions.insert_italic),  # type: ignore[attr-defined]
            ("Список", parent.text_insertions.insert_unordered_list),  # type: ignore[attr-defined]
            ("Цитата", lambda: parent.text_insertions.insert_text("> ")),  # type: ignore[attr-defined]
            ("Код", lambda: parent.text_insertions.insert_text("```\n```")),  # type: ignore[attr-defined]
            ("LaTeX inline", parent.text_insertions.insert_inline_latex),  # type: ignore[attr-defined]
            ("LaTeX block", parent.text_insertions.insert_block_latex),  # type: ignore[attr-defined]
            ("Ссылка", parent.text_insertions.insert_link),  # type: ignore[attr-defined]
            ("Изображение", parent.text_insertions.insert_image),  # type: ignore[attr-defined]
            ("Тема", parent._toggle_theme),  # type: ignore[attr-defined]
            ("Тема редактора", parent._toggle_editor_theme),  # type: ignore[attr-defined]
        ]

        for text, callback in actions:
            action = QAction(text, parent)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        toolbar.addSeparator()

        # -- Файловые действия --
        for text, callback in [
            ("Открыть", parent.file_io.open_file),  # type: ignore[attr-defined]
            ("Сохранить", parent.file_io.save_file),  # type: ignore[attr-defined]
            ("Экспорт в PDF", parent.file_export.export_to_pdf),  # type: ignore[attr-defined]
        ]:
            action = QAction(text, parent)
            action.triggered.connect(callback)
            toolbar.addAction(action)
            action = QAction(text, parent)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        self._build_font_controls(toolbar, parent)

        # -- Сброс шрифта --
        toolbar.addSeparator()
        reset_action = QAction("Сбросить шрифт", parent)
        reset_action.setToolTip("Сбросить шрифт и размер к значениям по умолчанию")
        reset_action.triggered.connect(parent._reset_font)  # type: ignore[attr-defined]
        toolbar.addAction(reset_action)

    def _on_heading_combo_activated(self) -> None:
        """Обработчик выбора уровня заголовка в комбобоксе."""
        if self._editor.heading_combo is not None:
            level = self._editor.heading_combo.currentIndex() + 1
            self._editor.text_insertions.insert_heading(level)

    def _build_font_controls(self, toolbar: QToolBar, parent: QMainWindow) -> None:
        """Создать комбобокс и кнопки управления шрифтом."""
        theme_mgr = parent.theme_manager  # type: ignore[attr-defined]

        font_combo = QComboBox()
        available_fonts = theme_mgr.get_available_fonts()
        font_combo.addItems(available_fonts)

        current_family = theme_mgr.font_family
        font_idx = font_combo.findText(current_family, Qt.MatchFlag.MatchExactly)

        if font_idx >= 0:
            font_combo.setCurrentIndex(font_idx)
        else:
            consolas_idx = font_combo.findText("Consolas", Qt.MatchFlag.MatchExactly)
            if consolas_idx >= 0:
                font_combo.setCurrentIndex(consolas_idx)
            else:
                font_combo.setCurrentIndex(0)

        font_combo.currentTextChanged.connect(parent._on_font_changed)  # type: ignore[attr-defined]
        font_combo.setMinimumWidth(160)
        toolbar.addWidget(font_combo)
        parent.font_combo = font_combo  # type: ignore[attr-defined]

        # -- Размер шрифта: + --
        font_increase_btn = QPushButton("+")
        font_increase_btn.setToolTip("Увеличить шрифт")
        font_increase_btn.setFixedWidth(32)
        font_increase_btn.clicked.connect(parent._increase_font)  # type: ignore[attr-defined]
        toolbar.addWidget(font_increase_btn)
        parent.font_increase_btn = font_increase_btn  # type: ignore[attr-defined]

        # -- Отображение размера шрифта --
        font_size_label = QLabel("11")
        font_size_label.setToolTip("Размер шрифта")
        font_size_label.setFixedWidth(30)
        font_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.addWidget(font_size_label)
        parent.font_size_label = font_size_label  # type: ignore[attr-defined]

        # -- Размер шрифта: - --
        font_decrease_btn = QPushButton("-")
        font_decrease_btn.setToolTip("Уменьшить шрифт")
        font_decrease_btn.setFixedWidth(32)
        font_decrease_btn.clicked.connect(parent._decrease_font)  # type: ignore[attr-defined]
        toolbar.addWidget(font_decrease_btn)
        parent.font_decrease_btn = font_decrease_btn  # type: ignore[attr-defined]


class MenuBuilder:
    """Создаёт меню: Файл, Правка, Вид, Справка."""

    def __init__(self, editor: MarkdownEditorPyQt) -> None:
        self._editor = editor

    def build(self) -> None:
        """Собрать все меню и добавить их в menubar editor."""
        parent: MarkdownEditorPyQt = self._editor
        menubar = parent.menuBar()
        assert menubar is not None

        self._build_file_menu(menubar, parent)
        self._build_edit_menu(menubar, parent)
        self._build_view_menu(menubar, parent)
        self._build_help_menu(menubar, parent)

    def _build_file_menu(self, menubar: QMenuBar, parent: MarkdownEditorPyQt) -> None:
        """Создать меню Файл."""
        file_menu = menubar.addMenu("Файл")
        assert file_menu is not None

        self._add_action(
            file_menu,
            "Новый",
            parent.file_ops.new_file,
            QKeySequence.StandardKey.New,
        )
        self._add_action(
            file_menu,
            "Открыть",
            parent.file_ops.open_file,
            QKeySequence.StandardKey.Open,
        )
        self._add_action(
            file_menu,
            "Сохранить",
            parent.file_ops.save_file,
            QKeySequence.StandardKey.Save,
        )
        self._add_action(file_menu, "Сохранить как...", parent.file_ops.save_file_as)
        file_menu.addSeparator()
        self._add_action(
            file_menu,
            "Закрыть",
            parent.close,
            QKeySequence.StandardKey.Close,
        )
        file_menu.addSeparator()
        self._add_action(file_menu, "Экспорт в HTML", parent.file_export.export_to_html)
        self._add_action(file_menu, "Экспорт в PDF", parent.file_export.export_to_pdf)
        self._add_action(
            file_menu, "Настройки PDF-экспорта...", parent._show_pdf_settings
        )
        file_menu.addSeparator()
        self._add_action(
            file_menu,
            "Выход",
            parent.close,
            QKeySequence.StandardKey.Quit,
        )

    def _build_edit_menu(self, menubar: QMenuBar, parent: MarkdownEditorPyQt) -> None:
        """Создать меню Правка."""
        edit_menu = menubar.addMenu("Правка")
        assert edit_menu is not None

        self._add_action(
            edit_menu,
            "Отменить",
            parent.editor.undo,
            QKeySequence.StandardKey.Undo,
        )
        self._add_action(
            edit_menu,
            "Повторить",
            parent.editor.redo,
            QKeySequence.StandardKey.Redo,
        )
        edit_menu.addSeparator()
        self._add_action(
            edit_menu,
            "Вырезать",
            parent.editor.cut,
            QKeySequence.StandardKey.Cut,
        )
        self._add_action(
            edit_menu,
            "Копировать",
            parent.editor.copy,
            QKeySequence.StandardKey.Copy,
        )
        self._add_action(
            edit_menu,
            "Вставить",
            parent.editor.paste,
            QKeySequence.StandardKey.Paste,
        )
        edit_menu.addSeparator()
        self._add_action(
            edit_menu,
            "Найти и заменить",
            parent._find_replace,
            QKeySequence.StandardKey.Find,
        )
        edit_menu.addSeparator()
        self._add_action(
            edit_menu,
            "Вставить изображение...",
            parent.text_insertions.insert_image,
        )

    def _build_view_menu(self, menubar: QMenuBar, parent: MarkdownEditorPyQt) -> None:
        """Создать меню Вид."""
        view_menu = menubar.addMenu("Вид")
        assert view_menu is not None

        self._add_action(view_menu, "Обновить предпросмотр", parent.update_preview)
        view_menu.addSeparator()

        # Темы предпросмотра
        self._add_action(view_menu, "Тема: светлая", lambda: parent.set_theme("light"))
        self._add_action(view_menu, "Тема: тёмная", lambda: parent.set_theme("dark"))
        self._add_action(
            view_menu, "Тема: контрастная", lambda: parent.set_theme("contrast")
        )
        view_menu.addSeparator()

        # Темы редактора
        self._add_action(
            view_menu,
            "Тема редактора: светлая",
            lambda: parent.set_editor_theme("light"),
        )
        self._add_action(
            view_menu, "Тема редактора: тёмная", lambda: parent.set_editor_theme("dark")
        )
        self._add_action(
            view_menu,
            "Тема редактора: контрастная",
            lambda: parent.set_editor_theme("contrast"),
        )
        view_menu.addSeparator()

        # Шрифт
        self._add_action(
            view_menu,
            "Увеличить шрифт",
            parent._increase_font,
            QKeySequence.StandardKey.ZoomIn,
        )
        self._add_action(
            view_menu,
            "Уменьшить шрифт",
            parent._decrease_font,
            QKeySequence.StandardKey.ZoomOut,
        )
        self._add_action(
            view_menu,
            "Сбросить шрифт",
            parent._reset_font,
            QKeySequence("Ctrl+0"),
        )

    def _build_help_menu(self, menubar: QMenuBar, parent: MarkdownEditorPyQt) -> None:
        """Создать меню Справка."""
        help_menu = menubar.addMenu("Справка")
        assert help_menu is not None

        self._add_action(help_menu, "О программе", parent._show_about)

    @staticmethod
    def _add_action(
        menu: QMenu,
        text: str,
        callback: Callable[[], None] | Callable[[], bool],  # type: ignore[type-arg]
        shortcut: QKeySequence | QKeySequence.StandardKey | None = None,
    ) -> None:
        """Добавить QAction в меню."""
        action = QAction(text, menu)
        if shortcut is not None:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        menu.addAction(action)
