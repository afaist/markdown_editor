"""Main MarkdownEditorPyQt class — thin wrapper assembling components."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow

from markdown_editor_pkg.editor_close import CloseHandler
from markdown_editor_pkg.editor_components import MenuBuilder, ToolbarBuilder, UIBuilder
from markdown_editor_pkg.editor_events import EventHandler
from markdown_editor_pkg.editor_find import FindReplaceHandler
from markdown_editor_pkg.editor_help import HelpHandler
from markdown_editor_pkg.editor_markdown_menu import MarkdownMenuBuilder
from markdown_editor_pkg.editor_pdf import PDFHandler
from markdown_editor_pkg.editor_session import SessionHandler
from markdown_editor_pkg.editor_themes import ThemeFontHandler
from markdown_editor_pkg.file_operations import EditorState, FileExport, FileIO
from markdown_editor_pkg.i18n import tr
from markdown_editor_pkg.latex_processor import LaTeXProcessor
from markdown_editor_pkg.markdown_renderer import MarkdownRenderer
from markdown_editor_pkg.resource_path import get_base_dir
from markdown_editor_pkg.scroll_sync import ScrollSyncManager
from markdown_editor_pkg.text_insertions import TextInsertions
from markdown_editor_pkg.themes import ThemesManager

if TYPE_CHECKING:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWidgets import (
        QComboBox,
        QFrame,
        QLabel,
        QPushButton,
        QSplitter,
        QStatusBar,
        QTextEdit,
    )

    from markdown_editor_pkg.editor_events import EventHandler
    from PyQt6.QtWebChannel import QWebChannel


class MarkdownEditorPyQt(QMainWindow):
    """Основной класс редактора Markdown с предпросмотром на PyQt6.

    Это тонкая обёртка, которая собирает компоненты и делегирует им работу.
    """

    def __init__(self) -> None:
        """Инициализация редактора: создание компонентов, таймеров и загрузка сессии.

        Создаёт все подмодули (UI, рендерер, обработчики), настраивает таймеры
        автосохранения и предпросмотра, затем инициализирует UI и загружает
        последнюю сессию.
        """
        super().__init__()
        self.setWindowTitle(tr("Markdown Editor (PyQt6)"))

        # Виджеты (заполняются UIBuilder)
        self.editor: QTextEdit
        self.preview: QWebEngineView
        self.splitter: QSplitter
        self.editor_frame: QFrame
        self.preview_frame: QFrame
        self._statusbar_ref: QStatusBar | None = None
        self.file_name_label: QLabel | None = None
        self.char_count_label: QLabel | None = None
        self.word_count_label: QLabel | None = None
        self.font_combo: QComboBox | None = None
        self.font_size_label: QLabel | None = None
        self.font_increase_btn: QPushButton | None = None
        self.font_decrease_btn: QPushButton | None = None
        self.heading_combo: QComboBox | None = None
        self.style_combo: QComboBox | None = None
        self.list_style_combo: QComboBox | None = None
        self.insert_combo: QComboBox | None = None
        self.export_combo: QComboBox | None = None
        self.preview_theme_label: QLabel | None = None
        self.editor_theme_label: QLabel | None = None

        # Scroll sync
        self.scroll_sync = ScrollSyncManager(self)

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

        # Загрузка настроек (темы, шрифт)
        self._load_settings()

        # Загрузка последней сессии
        self.session_handler.load_session()

    # ─── Публичный API компонентов (обёртки) ───────────────────────────

    def init_ui(self) -> None:
        """Инициализация интерфейса (делегирование компонентам)."""
        self.ui_builder.build()
        self.toolbar_builder.build()
        self.menu_builder.build()
        # Инициализация синхронизации прокрутки
        self.init_scroll_sync()

    def _load_settings(self) -> None:
        """Загрузить сохранённые настройки тем и шрифтов из Settings."""
        from markdown_editor_pkg.settings import Settings

        settings = Settings()

        # Тема предпросмотра
        saved_theme = settings.get("theme", "light")
        if saved_theme in ThemesManager._get_themes_css():
            self.theme_manager.set_preview_theme(saved_theme)

        # Тема редактора
        saved_editor_theme = settings.get("editor_theme", "light")
        if saved_editor_theme in ThemesManager._get_editor_styles():
            self.theme_manager.set_editor_theme(saved_editor_theme, self.editor, persist=False)

        # Обновить метки тем
        if self.preview_theme_label is not None:
            self.preview_theme_label.setText(
                f"{tr('Preview Theme')}: {self.theme_manager.theme_name.capitalize()}"
            )
        if self.editor_theme_label is not None:
            self.editor_theme_label.setText(
                f"{tr('Editor Theme')}: {self.theme_manager.editor_theme.capitalize()}"
            )

        # Шрифт
        saved_font = settings.get("editor_font", "Consolas")
        saved_font_size = settings.get("editor_font_size", 11)
        self.theme_manager.set_font(saved_font, saved_font_size, self.editor, persist=False)
        self.theme_font_handler._update_font_size_label()
        if self.font_combo is not None:
            font_idx = self.font_combo.findText(saved_font, Qt.MatchFlag.MatchExactly)
            if font_idx >= 0:
                self.font_combo.setCurrentIndex(font_idx)

        # Размер окна
        from PyQt6.QtGui import QGuiApplication

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            screen_size = screen.size()
        else:
            screen_size = None

        saved_w = settings.get("window_width", 1400)
        saved_h = settings.get("window_height", 800)

        if screen_size is not None:
            if saved_w > screen_size.width() or saved_h > screen_size.height():
                self.showFullScreen()
            else:
                self.resize(saved_w, saved_h)
        else:
            self.resize(saved_w, saved_h)

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

    def on_cursor_position_changed(self) -> None:
        """Синхронизация предпросмотра с позицией курсора (делегирование)."""
        self.event_handler.on_cursor_position_changed()

    def init_scroll_sync(self) -> None:
        """Инициализация синхронизации прокрутки между редактором и превью."""
        self.scroll_sync.init()

    def on_preview_scroll(self, scroll_pct: float) -> None:
        """Обработчик скролла превью (для обратной совместимости)."""
        self.event_handler.on_preview_scroll(scroll_pct)

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

    def _show_shortcuts(self) -> None:
        self.help_handler.show_shortcuts()

    def _show_markdown_help(self) -> None:
        self.help_handler.show_markdown_help()

    def _show_restart_notification(self) -> None:
        """Show a notification that UI text will update on next restart."""
        from PyQt6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(tr("Language Changed"))
        msg.setText(tr("Language changed. Some UI elements will update after restart."))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _show_gpu_restart_notification(self) -> None:
        """Show a notification that GPU settings require a restart."""
        from PyQt6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(tr("GPU Acceleration Changed"))
        msg.setText(
            tr(
                "GPU acceleration setting changed. The application must be restarted for changes to take effect."
            )
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    # Синхронизация редактора и предпросмотра
    def _scroll_preview_to_cursor(self) -> None:
        """Прокручивает предпросмотр к строке, где находится курсор.

        Вызывается из update_preview после обновления HTML, чтобы ID заголовков
        уже были доступны в DOM.
        """
        try:
            cursor = self.editor.textCursor()
            block = cursor.block()
            line_text = block.text().strip()
            if not line_text or not line_text.startswith("#"):
                return

            # Генерируем якорь как python-markdown toc extension:
            # lowercase, пробелы -> -, только алфавит+цифры+дефисы
            md_anchor = line_text.lstrip("#").strip().lower()
            md_anchor = md_anchor.replace(" ", "-")
            md_anchor = "".join(c if c.isalnum() or c == "-" else "" for c in md_anchor)
            while "--" in md_anchor:
                md_anchor = md_anchor.replace("--", "-")
            md_anchor = md_anchor.strip("-")
            if not md_anchor:
                return

            js = f"""
(function() {{
    var anchor = {json.dumps(md_anchor)};
    var el = document.getElementById(anchor);
    if (!el) {{
        var all = document.querySelectorAll('[id]');
        for (var i = 0; i < all.length; i++) {{
            if (all[i].id === anchor) {{
                el = all[i];
                break;
            }}
        }}
    }}
    if (el) {{
        el.scrollIntoView({{behavior: 'smooth', block: 'start'}});
    }}
}})();
"""
            if self.preview is not None:
                page = self.preview.page()
                if page is not None:
                    page.runJavaScript(js)

        except Exception:
            logger.exception("Scroll sync error in _scroll_preview_to_cursor")

    # Закрытие
    def closeEvent(self, event_: QCloseEvent | None) -> None:
        """Обработчик закрытия окна: проверка чистоты и сохранение сессии."""
        self.close_handler.on_close(event_)

    # ─── Обратная совместимость (для старых тестов) ─────────────────────

    @property
    def current_file(self) -> str | None:
        return self._file_state.current_file

    @current_file.setter
    def current_file(self, value: str | None) -> None:
        """Установить текущий путь к файлу."""
        self._file_state.current_file = value

    @property
    def is_dirty(self) -> bool:
        return self._file_state.is_dirty

    @is_dirty.setter
    def is_dirty(self, value: bool) -> None:
        """Установить флаг наличия несохранённых изменений."""
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
    def display_math_cache(self) -> list:
        """Для совместимости: кэш блочных формул."""
        return self.latex_processor.display_math_cache

    @display_math_cache.setter
    def display_math_cache(self, value: list) -> None:
        """Установить кэш блочных формул LaTeX."""
        self.latex_processor.display_math_cache = value

    @property
    def inline_math_cache(self) -> list:
        """Для совместимости: кэш встроенных формул."""
        return self.latex_processor.inline_math_cache

    @inline_math_cache.setter
    def inline_math_cache(self, value: list) -> None:
        """Установить кэш встроенных формул LaTeX."""
        self.latex_processor.inline_math_cache = value

    def process_latex_before_markdown(self, text: str) -> str:
        """Для совместимости: обработка LaTeX перед конвертацией Markdown."""
        return self.latex_processor.process(text)

    def render_markdown(self, text: str, theme_name: str = "light") -> str:
        """Для совместимости: рендеринг Markdown в HTML."""
        return self.renderer.render(
            text,
            theme_name=theme_name,
            base_dir=get_base_dir(),
        )

    def toggle_theme(self) -> None:
        """Для совместимости: переключить тему предпросмотра."""
        self._toggle_theme()
