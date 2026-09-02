"""Главный класс MarkdownEditorPyQt — тонкая обёртка, собирающая компоненты."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QMessageBox

from markdown_editor_pkg.themes import ThemesManager
from markdown_editor_pkg.markdown_renderer import MarkdownRenderer
from markdown_editor_pkg.file_operations import FileIO, FileExport, EditorState
from markdown_editor_pkg.text_insertions import TextInsertions
from markdown_editor_pkg.latex_processor import LaTeXProcessor
from markdown_editor_pkg.editor_components import UIBuilder, ToolbarBuilder, MenuBuilder
from markdown_editor_pkg.editor_markdown_menu import MarkdownMenuBuilder
from markdown_editor_pkg.editor_events import EventHandler
from markdown_editor_pkg.editor_pdf import PDFHandler
from markdown_editor_pkg.editor_session import SessionHandler
from markdown_editor_pkg.editor_help import HelpHandler
from markdown_editor_pkg.editor_themes import ThemeFontHandler
from markdown_editor_pkg.editor_find import FindReplaceHandler
from markdown_editor_pkg.editor_close import CloseHandler
from markdown_editor_pkg.editor_keypress import MarkdownTextEdit

if TYPE_CHECKING:
    from PyQt6.QtWidgets import (
        QTextEdit,
        QSplitter,
        QFrame,
        QStatusBar,
        QLabel,
        QComboBox,
        QPushButton,
    )
    from PyQt6.QtWebEngineWidgets import QWebEngineView


class MarkdownEditorPyQt(QMainWindow):
    """Основной класс редактора Markdown с предпросмотром на PyQt6.

    Это тонкая обёртка, которая собирает компоненты и делегирует им работу.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Markdown Editor (PyQt6)")
        self.resize(1200, 800)

        # Виджеты (заполняются UIBuilder)
        self.editor: QTextEdit  # type: ignore[misc]
        self.preview: QWebEngineView  # type: ignore[misc]
        self.splitter: QSplitter  # type: ignore[misc]
        self.editor_frame: QFrame  # type: ignore[misc]
        self.preview_frame: QFrame  # type: ignore[misc]
        self._statusbar_ref: QStatusBar | None = None  # type: ignore[misc]
        self.file_name_label: QLabel | None = None  # type: ignore[misc]
        self.char_count_label: QLabel | None = None  # type: ignore[misc]
        self.word_count_label: QLabel | None = None  # type: ignore[misc]
        self.font_combo: QComboBox | None = None  # type: ignore[misc]
        self.font_size_label: QLabel | None = None  # type: ignore[misc]
        self.font_increase_btn: QPushButton | None = None  # type: ignore[misc]
        self.font_decrease_btn: QPushButton | None = None  # type: ignore[misc]
        self.heading_combo: QComboBox | None = None  # type: ignore[misc]
        self.style_combo: QComboBox | None = None  # type: ignore[misc]
        self.list_style_combo: QComboBox | None = None  # type: ignore[misc]

        # Подмодули
        self.theme_manager = ThemesManager()
        self.renderer = MarkdownRenderer(themes=self.theme_manager)
        self.latex_processor = LaTeXProcessor()
        # EditorState — единый контекст состояния файлов
        self._file_state = EditorState()

        self.file_io = FileIO(
            editor=self, statusbar=None, renderer=self.renderer, state=self._file_state
        )
        self.file_export = FileExport(
            editor=self, statusbar=None, renderer=self.renderer, state=self._file_state
        )

        # file_ops для обратной совместимости
        self.file_ops = self.file_io
        self.text_insertions = TextInsertions(editor=self)

        # Таймеры
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.file_ops.save_file)
        self.auto_save_timer.setSingleShot(True)

        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)

        # Компоненты
        self.ui_builder = UIBuilder(self)
        self.toolbar_builder = ToolbarBuilder(self)
        self.menu_builder = MenuBuilder(self)
        self.markdown_menu_builder = MarkdownMenuBuilder(self)
        self.event_handler = EventHandler(self)
        self.pdf_handler = PDFHandler(self)
        self.session_handler = SessionHandler(self)
        self.help_handler = HelpHandler(self)
        self.theme_font_handler = ThemeFontHandler(self)
        self.find_replace_handler = FindReplaceHandler(self)
        self.close_handler = CloseHandler(self)

        # Инициализация
        self.init_ui()

        # Подменяю ссылку на statusbar в file_ops
        self.file_io._statusbar = self._statusbar_ref
        self.file_export._statusbar = self._statusbar_ref

        # Загрузка последней сессии
        self.session_handler.load_session()

    # ─── Публичный API компонентов (обёртки) ───────────────────────────

    def init_ui(self) -> None:
        """Инициализация интерфейса (делегирование компонентам)."""
        self.ui_builder.build()
        self.toolbar_builder.build()
        self.menu_builder.build()
        self.markdown_menu_builder.build()

    # Обработчики событий
    def on_text_change(self) -> None:
        """Обработка изменения текста (делегирование)."""
        self.event_handler.on_text_change()

    def update_file_status(self) -> None:
        """Обновить статус файла (делегирование)."""
        self.event_handler.update_file_status()

    def update_preview(self) -> None:
        """Обновить предпросмотр (делегирование)."""
        self.event_handler.update_preview()

    def update_char_count(self) -> None:
        """Обновить счётчики (делегирование)."""
        self.event_handler.update_char_count()

    def _set_editor_text_without_dirty(self, text: str) -> None:
        """Установка текста без is_dirty (делегирование)."""
        self.event_handler.set_editor_text_without_dirty(text)

    # Темы и шрифты
    def _toggle_theme(self) -> None:
        self.theme_font_handler.toggle_theme()

    def set_theme(self, theme_name: str) -> None:
        """Установить тему предпросмотра."""
        self.theme_font_handler.set_theme(theme_name)

    def _toggle_editor_theme(self) -> None:
        self.theme_font_handler.toggle_editor_theme()

    def set_editor_theme(self, theme_name: str) -> None:
        """Установить тему редактора."""
        self.theme_font_handler.set_editor_theme(theme_name)

    def _on_font_changed(self, family: str) -> None:
        self.theme_font_handler.on_font_changed(family)

    def _increase_font(self) -> None:
        self.theme_font_handler.increase_font()

    def _decrease_font(self) -> None:
        self.theme_font_handler.decrease_font()

    def _reset_font(self) -> None:
        self.theme_font_handler.reset_font()

    # PDF
    def _show_pdf_settings(self) -> None:
        self.pdf_handler.show_pdf_settings()

    # Поиск
    def _find_replace(self) -> None:
        self.find_replace_handler.find_replace()

    # Сессия
    def save_last_session(self, filepath: str) -> None:
        """Сохранить путь к файлу в сессии (обёртка)."""
        self.session_handler.save_session(filepath)

    def load_last_session(self) -> None:
        """Загрузить последнюю сессию (обёртка)."""
        self.session_handler.load_session()

    # Справка
    def _show_about(self) -> None:
        self.help_handler.show_about()

    # Закрытие
    def closeEvent(self, event_: QCloseEvent) -> None:  # type: ignore[override]
        self.close_handler.on_close(event_)

    # ─── Обратная совместимость (для старых тестов) ─────────────────────

    @property
    def current_file(self) -> str | None:
        return self._file_state.current_file

    @current_file.setter
    def current_file(self, value: str | None) -> None:
        self._file_state.current_file = value

    @property
    def is_dirty(self) -> bool:
        return self._file_state.is_dirty

    @is_dirty.setter
    def is_dirty(self, value: bool) -> None:
        self._file_state.is_dirty = value

    @property
    def theme_name(self) -> str:
        """Для совместимости: имя текущей темы предпросмотра."""
        return self.theme_manager.theme_name

    @property
    def editor_theme(self) -> str:
        """Для совместимости: имя текущей темы редактора."""
        return self.theme_manager.editor_theme

    @property
    def themes(self) -> dict:
        """Для совместимости: словарь CSS-тем."""
        return self.theme_manager.THEMES_CSS

    @property
    def display_math_cache(self) -> list:
        """Для совместимости: кэш блочных формул."""
        return self.latex_processor.display_math_cache

    @display_math_cache.setter
    def display_math_cache(self, value: list) -> None:
        self.latex_processor.display_math_cache = value

    @property
    def inline_math_cache(self) -> list:
        """Для совместимости: кэш встроенных формул."""
        return self.latex_processor.inline_math_cache

    @inline_math_cache.setter
    def inline_math_cache(self, value: list) -> None:
        self.latex_processor.inline_math_cache = value

    def process_latex_before_markdown(self, text: str) -> str:
        """Для совместимости: обработка LaTeX перед конвертацией Markdown."""
        return self.latex_processor.process(text)

    def render_markdown(self, text: str, theme_name: str = "light") -> str:
        """Для совместимости: рендеринг Markdown в HTML."""
        return self.renderer.render(
            text,
            theme_name=theme_name,
            base_dir=os.path.dirname(os.path.abspath(__file__)),
        )

    def toggle_theme(self) -> None:
        """Для совместимости: переключить тему предпросмотра."""
        self._toggle_theme()
