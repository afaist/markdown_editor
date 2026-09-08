"""UI combiners for MarkdownEditorPyQt — building the interface from components.

Contains:
- UIBuilder — creates main UI (splitter, editor, preview, statusbar)
- ToolbarBuilder — creates the toolbar
- MenuBuilder — creates menus (File, Edit, View, Help)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QKeySequence
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
)

from markdown_editor_pkg.editor_keypress import MarkdownTextEdit
from markdown_editor_pkg.i18n import tr

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class UIBuilder:
    """Создаёт основной UI: сплиттер, редактор, предпросмотр, статусбар."""

    def __init__(self, editor: MarkdownEditorPyQt) -> None:
        """Инициализация сборщика UI.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
        """
        self._editor = editor

    def build(self, parent: QMainWindow | None = None) -> None:
        """Собрать весь UI и добавить его в parent (MarkdownEditorPyQt).

        Создаёт сплиттер с редактором и превью, строит строку состояния
        и подключает сигналы editor.textChanged.

        Args:
            parent: Родительский QMainWindow; по умолчанию используется self._editor.
        """
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

        editor_label = QLabel(tr("Editor Markdown"))
        editor_label.setStyleSheet("background-color: #f0f0f0; color: #333333;")
        editor_label.setMinimumHeight(25)
        editor_label.setMaximumHeight(25)
        editor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor_layout.addWidget(editor_label)

        text_edit = MarkdownTextEdit()
        text_edit.setFont(QFont("Consolas", 11))
        self._editor.theme_manager.set_editor_theme("light", text_edit, persist=False)
        editor_layout.addWidget(text_edit)
        self._editor.editor = text_edit  # type: ignore[attr-defined]

        splitter.addWidget(editor_frame)

        # -- Предпросмотр --
        preview_frame = QFrame()
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(0)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_frame.setLayout(preview_layout)

        preview_label = QLabel(tr("Preview"))
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

        char_count_label = QLabel(tr("Characters: 0"))
        word_count_label = QLabel(tr("Words: 0"))
        file_name_label = QLabel("")
        file_name_label.setMinimumWidth(250)
        theme_label = QLabel(f"{tr('Theme')}: Light")
        theme_label.setMinimumWidth(150)

        statusbar.addPermanentWidget(file_name_label)
        statusbar.addPermanentWidget(char_count_label)
        statusbar.addPermanentWidget(word_count_label)
        statusbar.addPermanentWidget(theme_label)

        self._editor.file_name_label = file_name_label  # type: ignore[attr-defined]
        self._editor.char_count_label = char_count_label  # type: ignore[attr-defined]
        self._editor.word_count_label = word_count_label  # type: ignore[attr-defined]
        self._editor.theme_label = theme_label  # type: ignore[attr-defined]

    def _connect_signals(self, parent: QMainWindow) -> None:
        """Подключить сигналы editor.textChanged."""
        parent.editor.textChanged.connect(parent.on_text_change)  # type: ignore[attr-defined]
        parent.editor.textChanged.connect(parent.update_char_count)  # type: ignore[attr-defined]
        parent.editor.textChanged.connect(parent.update_file_status)  # type: ignore[attr-defined]


class ToolbarBuilder:
    """Создаёт панель инструментов (QToolBar) с кнопками форматирования."""

    def __init__(self, editor: MarkdownEditorPyQt) -> None:
        """Инициализация сборщика панели инструментов.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
        """
        self._editor = editor

    def build(self) -> None:
        """Собрать панель инструментов с комбобоксами, кнопками и действиями.

        Создаёт QToolBar с комбобоксами для заголовков, стилей, типов списков,
        кнопками форматирования, файловых действий и элементов управления шрифтом.
        """

        # style_sheet_lbl = "color: white;"
        style_sheet_lbl = ""

        parent = self._editor
        toolbar = QToolBar(tr("Formatting"))
        parent.addToolBar(toolbar)

        lbl_headers = QLabel(tr("Headings: "))
        lbl_headers.setStyleSheet(style_sheet_lbl)
        lbl_headers.adjustSize()
        toolbar.addWidget(lbl_headers)

        # -- Выбор уровня заголовка --
        heading_combo = QComboBox()
        for lvl in range(1, 7):
            heading_combo.addItem(f"H{lvl}")
        heading_combo.setCurrentIndex(0)
        heading_combo.setToolTip(tr("Heading level (1–6)"))
        heading_combo.activated.connect(self._on_heading_combo_activated)  # type: ignore[attr-defined]

        heading_combo.setMinimumWidth(80)
        toolbar.addWidget(heading_combo)
        parent.heading_combo = heading_combo  # type: ignore[attr-defined]
        toolbar.addSeparator()

        lbl_formating = QLabel(tr("Styles: "))
        lbl_formating.setStyleSheet(style_sheet_lbl)
        lbl_formating.adjustSize()
        toolbar.addWidget(lbl_formating)

        # -- Комбобокс стилей --
        style_combo = QComboBox()
        style_combo.addItems([tr("Bold"), tr("Italic"), tr("Strikethrough"), tr("Code")])
        style_combo.setMinimumWidth(120)
        style_combo.setToolTip(tr("Select formatting style"))
        style_combo.activated.connect(self._on_style_combo_activated)  # type: ignore[attr-defined]
        toolbar.addWidget(style_combo)
        parent.style_combo = style_combo  # type: ignore[attr-defined]
        toolbar.addSeparator()

        # -- Список: комбобокс стилей --
        lbl_list = QLabel(tr("List: "))
        lbl_list.setStyleSheet(style_sheet_lbl)
        lbl_list.adjustSize()
        toolbar.addWidget(lbl_list)

        list_style_combo = QComboBox()
        list_style_combo.addItems([tr("Bulleted"), tr("Numbered"), tr("Task List")])
        list_style_combo.setMinimumWidth(120)
        list_style_combo.setToolTip(tr("Select list style"))
        list_style_combo.activated.connect(self._on_list_style_combo_activated)  # type: ignore[attr-defined]
        toolbar.addWidget(list_style_combo)
        parent.list_style_combo = list_style_combo  # type: ignore[attr-defined]
        toolbar.addSeparator()

        # -- Форматирование --
        actions: list[tuple[str, Callable[[], None]]] = [
            (tr("Quote"), lambda: parent.text_insertions.insert_text("> ")),  # type: ignore[attr-defined]
            (tr("Code"), lambda: parent.text_insertions.insert_text("```\n```")),  # type: ignore[attr-defined]
            (tr("LaTeX inline"), parent.text_insertions.insert_inline_latex),  # type: ignore[attr-defined]
            (tr("LaTeX block"), parent.text_insertions.insert_block_latex),  # type: ignore[attr-defined]
            (tr("Link"), parent.text_insertions.insert_link),  # type: ignore[attr-defined]
            (tr("Image"), parent.text_insertions.insert_image),  # type: ignore[attr-defined]
            (tr("Theme"), parent._toggle_theme),  # type: ignore[attr-defined]
            (tr("Editor Theme"), parent._toggle_editor_theme),  # type: ignore[attr-defined]
        ]

        for text, callback in actions:
            action = QAction(text, parent)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        toolbar.addSeparator()

        # -- Файловые действия --
        for text, callback in [
            (tr("Open"), parent.file_io.open_file),  # type: ignore[attr-defined]
            (tr("Save"), parent.file_io.save_file),  # type: ignore[attr-defined]
            (tr("Export to PDF"), parent.file_export.export_to_pdf),
        ]:
            action = QAction(text, parent)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        self._build_font_controls(toolbar, parent)

        # -- Сброс шрифта --
        toolbar.addSeparator()
        reset_action = QAction(tr("Reset Font"), parent)
        reset_action.setToolTip(tr("Reset font and size to defaults"))
        reset_action.triggered.connect(parent._reset_font)  # type: ignore[attr-defined]
        toolbar.addAction(reset_action)

    def _on_heading_combo_activated(self) -> None:
        """Обработчик выбора уровня заголовка в комбобоксе."""
        if self._editor.heading_combo is not None:
            level = self._editor.heading_combo.currentIndex() + 1
            self._editor.text_insertions.insert_heading(level)

    def _on_style_combo_activated(self) -> None:
        """Обработчик выбора стиля в комбобоксе."""
        parent = self._editor
        if parent.style_combo is not None:
            idx = parent.style_combo.currentIndex()
            if idx == 0:
                parent.text_insertions.insert_bold()
            elif idx == 1:
                parent.text_insertions.insert_italic()
            elif idx == 2:
                parent.text_insertions.insert_strikethrough()
            elif idx == 3:
                parent.text_insertions.insert_inline_code()

    def _on_list_style_combo_activated(self) -> None:
        """Обработчик выбора стиля списка в комбобоксе."""
        parent = self._editor
        if parent.list_style_combo is not None:
            idx = parent.list_style_combo.currentIndex()
            if idx == 0:
                parent.text_insertions.insert_unordered_list()
            elif idx == 1:
                parent.text_insertions.insert_ordered_list()
            elif idx == 2:
                parent.text_insertions.insert_task_list()

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
        font_increase_btn.setToolTip(tr("Increase font size"))
        font_increase_btn.setFixedWidth(32)
        font_increase_btn.clicked.connect(parent._increase_font)  # type: ignore[attr-defined]
        toolbar.addWidget(font_increase_btn)
        parent.font_increase_btn = font_increase_btn  # type: ignore[attr-defined]

        # -- Отображение размера шрифта --
        font_size_label = QLabel("11")
        font_size_label.setToolTip(tr("Font size"))
        font_size_label.setFixedWidth(30)
        font_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.addWidget(font_size_label)
        parent.font_size_label = font_size_label  # type: ignore[attr-defined]

        # -- Размер шрифта: - --
        font_decrease_btn = QPushButton("-")
        font_decrease_btn.setToolTip(tr("Decrease font size"))
        font_decrease_btn.setFixedWidth(32)
        font_decrease_btn.clicked.connect(parent._decrease_font)  # type: ignore[attr-defined]
        toolbar.addWidget(font_decrease_btn)
        parent.font_decrease_btn = font_decrease_btn  # type: ignore[attr-defined]


class MenuBuilder:
    """Создаёт меню: Файл, Правка, Вид, Справка."""

    def __init__(self, editor: MarkdownEditorPyQt) -> None:
        """Инициализация сборщика меню.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
        """
        self._editor = editor

    def build(self) -> None:
        """Собрать все меню (File, Edit, View, Markdown, Help) и добавить в menubar."""
        parent: MarkdownEditorPyQt = self._editor
        menubar = parent.menuBar()
        assert menubar is not None

        self._build_file_menu(menubar, parent)
        self._build_edit_menu(menubar, parent)
        self._build_view_menu(menubar, parent)
        # Markdown menu must be before Help (Help is always last)
        self._editor.markdown_menu_builder.build()
        self._build_help_menu(menubar, parent)

    def _build_file_menu(self, menubar: QMenuBar, parent: MarkdownEditorPyQt) -> None:
        """Create File menu."""
        file_menu = menubar.addMenu(tr("File"))
        assert file_menu is not None

        self._add_action(
            file_menu,
            tr("New"),
            parent.file_ops.new_file,
            QKeySequence.StandardKey.New,
        )
        self._add_action(
            file_menu,
            tr("Open"),
            parent.file_ops.open_file,
            QKeySequence.StandardKey.Open,
        )
        self._add_action(
            file_menu,
            tr("Save"),
            parent.file_ops.save_file,
            QKeySequence.StandardKey.Save,
        )
        self._add_action(file_menu, tr("Save As..."), parent.file_ops.save_file_as)
        file_menu.addSeparator()
        self._add_action(
            file_menu,
            tr("Close"),
            parent.close,
            QKeySequence.StandardKey.Close,
        )
        file_menu.addSeparator()
        self._add_action(file_menu, tr("Export to HTML"), parent.file_export.export_to_html)
        self._add_action(file_menu, tr("Export to PDF"), parent.file_export.export_to_pdf)
        self._add_action(file_menu, tr("PDF Export Settings..."), parent._show_pdf_settings)
        file_menu.addSeparator()
        self._add_action(
            file_menu,
            tr("Exit"),
            parent.close,
            QKeySequence.StandardKey.Quit,
        )

    def _build_edit_menu(self, menubar: QMenuBar, parent: MarkdownEditorPyQt) -> None:
        """Create Edit menu."""
        edit_menu = menubar.addMenu(tr("Edit"))
        assert edit_menu is not None

        self._add_action(
            edit_menu,
            tr("Undo"),
            parent.editor.undo,
            QKeySequence.StandardKey.Undo,
        )
        self._add_action(
            edit_menu,
            tr("Redo"),
            parent.editor.redo,
            QKeySequence.StandardKey.Redo,
        )
        edit_menu.addSeparator()
        self._add_action(
            edit_menu,
            tr("Cut"),
            parent.editor.cut,
            QKeySequence.StandardKey.Cut,
        )
        self._add_action(
            edit_menu,
            tr("Copy"),
            parent.editor.copy,
            QKeySequence.StandardKey.Copy,
        )
        self._add_action(
            edit_menu,
            tr("Paste"),
            parent.editor.paste,
            QKeySequence.StandardKey.Paste,
        )
        edit_menu.addSeparator()
        self._add_action(
            edit_menu,
            tr("Find and Replace"),
            parent._find_replace,
            QKeySequence.StandardKey.Find,
        )
        edit_menu.addSeparator()
        self._add_action(
            edit_menu,
            tr("Insert Image..."),
            parent.text_insertions.insert_image,
        )

    def _build_view_menu(self, menubar: QMenuBar, parent: MarkdownEditorPyQt) -> None:
        """Создать меню Вид."""
        view_menu = menubar.addMenu(tr("View"))
        assert view_menu is not None

        self._add_action(view_menu, tr("Refresh Preview"), parent.update_preview)
        view_menu.addSeparator()

        # Preview themes
        self._add_action(view_menu, tr("Theme: Light"), lambda: parent.set_theme("light"))
        self._add_action(view_menu, tr("Theme: Dark"), lambda: parent.set_theme("dark"))
        self._add_action(view_menu, tr("Theme: Contrast"), lambda: parent.set_theme("contrast"))
        view_menu.addSeparator()
        self._add_action(view_menu, tr("Theme: Monokai"), lambda: parent.set_theme("monokai"))
        self._add_action(view_menu, tr("Theme: Dracula"), lambda: parent.set_theme("dracula"))
        self._add_action(view_menu, tr("Theme: One Dark"), lambda: parent.set_theme("one-dark"))
        self._add_action(
            view_menu, tr("Theme: GitHub Dark"), lambda: parent.set_theme("github-dark")
        )
        self._add_action(
            view_menu, tr("Theme: Solarized Dark"), lambda: parent.set_theme("solarized-dark")
        )
        view_menu.addSeparator()

        # Editor themes
        self._add_action(
            view_menu,
            tr("Editor Theme: Light"),
            lambda: parent.set_editor_theme("light"),
        )
        self._add_action(
            view_menu, tr("Editor Theme: Dark"), lambda: parent.set_editor_theme("dark")
        )
        self._add_action(
            view_menu,
            tr("Editor Theme: Contrast"),
            lambda: parent.set_editor_theme("contrast"),
        )
        view_menu.addSeparator()
        self._add_action(
            view_menu,
            tr("Editor Theme: Monokai"),
            lambda: parent.set_editor_theme("monokai"),
        )
        self._add_action(
            view_menu,
            tr("Editor Theme: Dracula"),
            lambda: parent.set_editor_theme("dracula"),
        )
        self._add_action(
            view_menu,
            tr("Editor Theme: One Dark"),
            lambda: parent.set_editor_theme("one-dark"),
        )
        self._add_action(
            view_menu,
            tr("Editor Theme: GitHub Dark"),
            lambda: parent.set_editor_theme("github-dark"),
        )
        self._add_action(
            view_menu,
            tr("Editor Theme: Solarized Dark"),
            lambda: parent.set_editor_theme("solarized-dark"),
        )
        view_menu.addSeparator()

        # Font
        self._add_action(
            view_menu,
            tr("Increase Font"),
            parent._increase_font,
            QKeySequence.StandardKey.ZoomIn,
        )
        self._add_action(
            view_menu,
            tr("Decrease Font"),
            parent._decrease_font,
            QKeySequence.StandardKey.ZoomOut,
        )
        self._add_action(
            view_menu,
            tr("Reset Font"),
            parent._reset_font,
            QKeySequence("Ctrl+0"),
        )
        view_menu.addSeparator()

        # Language selector
        from markdown_editor_pkg.i18n import get_available_languages, load_language
        from markdown_editor_pkg.settings import Settings

        lang_settings = Settings()
        lang_menu = view_menu.addMenu(tr("Language"))
        for lang in get_available_languages():
            lang_action = QAction(lang["name"], parent)
            lang_action.setCheckable(True)
            current_lang = lang_settings.get("language", "en")
            if lang["code"] == current_lang:
                lang_action.setChecked(True)

            def _make_lang_callback(code: str) -> Callable[[], None]:
                def _callback() -> None:
                    lang_settings.set("language", code)
                    load_language(code)
                    parent._show_restart_notification()

                return _callback

            lang_action.triggered.connect(_make_lang_callback(lang["code"]))
            assert lang_menu is not None
            lang_menu.addAction(lang_action)

    def _build_help_menu(self, menubar: QMenuBar, parent: MarkdownEditorPyQt) -> None:
        """Создать меню Справка."""
        help_menu = menubar.addMenu(tr("Help"))
        assert help_menu is not None

        self._add_action(help_menu, tr("About"), parent._show_about)
        self._add_action(help_menu, tr("Keyboard Shortcuts"), parent._show_shortcuts)
        self._add_action(help_menu, tr("Markdown Help"), parent._show_markdown_help)

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
