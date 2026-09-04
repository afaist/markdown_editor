"""Главный класс MarkdownEditorPyQt — тонкая обёртка, собирающая компоненты."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

from PyQt6.QtCore import QTimer
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
from markdown_editor_pkg.latex_processor import LaTeXProcessor
from markdown_editor_pkg.markdown_renderer import MarkdownRenderer
from markdown_editor_pkg.resource_path import get_base_dir
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
        # Инициализация синхронизации прокрутки
        self.init_scroll_sync()

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
        # Подключаем скролл редактора
        vbar = self.editor.verticalScrollBar()
        if vbar is not None:
            vbar.valueChanged.connect(self.event_handler.sync_scroll_from_editor)

        # Инжектим JavaScript для отслеживания скролла в превью
        self._inject_scroll_tracker_js()

    def _inject_scroll_tracker_js(self) -> None:
        """Инжектит JavaScript для отслеживания скролла в QWebEngineView."""
        if self.preview is None:
            return

        page = self.preview.page()
        if page is None:
            return

        # Создаём объект-мост для передачи событий из JS в PyQt
        from PyQt6.QtCore import QObject, pyqtSlot
        from PyQt6.QtWebChannel import QWebChannel

        class ScrollBridge(QObject):
            """Мост между JavaScript и PyQt для событий скролла."""

            _handler: EventHandler
            _isScrolling: bool = False  # type: ignore[misc]

            @pyqtSlot(float)
            def onPreviewScroll(self, scroll_pct: float) -> None:
                self._handler.on_preview_scroll(scroll_pct)  # type: ignore[attr-defined]

            @pyqtSlot()
            def onScrollFromEditor(self) -> None:
                """Устанавливает флаг, что скролл инициирован из редактора."""
                self._handler._scroll_from_editor = True  # type: ignore[attr-defined]

        self._scroll_bridge = ScrollBridge()
        self._scroll_bridge._handler = self.event_handler  # type: ignore[attr-defined]

        # Создаём QWebChannel и регистрируем объект
        self._scroll_channel = QWebChannel()
        self._scroll_channel.registerObject("qt_object", self._scroll_bridge)

        # Запускаем JS-трекер сразу (без ожидания loadFinished)
        # Это нужно, потому что setHtml не вызывает loadFinished
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(500, lambda: self._run_scroll_tracker())

    def _run_scroll_tracker(self) -> None:
        """Запускает JS-трекер скролла."""
        if self.preview is None:
            return

        page = self.preview.page()
        if page is None:
            return

        # Регистрируем QWebChannel
        page.setWebChannel(self._scroll_channel)  # type: ignore[union-attr]

        # Запускаем JS-трекер (он сам подождёт появления qt_object)
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(100, lambda: page.runJavaScript(self._get_scroll_js()))  # type: ignore[union-attr]

    def _register_scroll_channel(self) -> None:
        """Регистрирует QWebChannel при обновлении превью."""
        if self.preview is None:
            return

        page = self.preview.page()
        if page is None:
            return

        # Регистрируем QWebChannel
        page.setWebChannel(self._scroll_channel)  # type: ignore[union-attr]

        # Запускаем JS-трекер (он сам подождёт появления qt_object)
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(50, lambda: page.runJavaScript(self._get_scroll_js()))  # type: ignore[union-attr]

    def _check_and_init_scroll_tracker(self, page) -> None:
        """Проверяет существование qt_object и инициализирует трекер."""
        page.runJavaScript(self._get_scroll_js())

    def _get_scroll_js(self) -> str:
        """Возвращает JavaScript-код для отслеживания скролла."""
        return """
(function() {
    var lastPct = -1;
    var bridge = null;
    var scrollPollingStarted = false;

    function startPolling() {
        if (scrollPollingStarted) return;
        scrollPollingStarted = true;

        // Опрос скролла каждые 100мс вместо событий scroll
        setInterval(function() {
            var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            var scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            var pct = scrollHeight > 0 ? scrollTop / scrollHeight : 0;

            if (Math.abs(pct - lastPct) > 0.001) {
                lastPct = pct;
                // Не отправляем событие, если скролл инициирован из редактора
                if (bridge && typeof bridge.onPreviewScroll === 'function' && !bridge._isScrolling) {
                    try {
                        bridge.onPreviewScroll(pct);
                    } catch(e) {
                        // Игнорируем ошибки
                    }
                }
            }
        }, 100);
    }

    // Ждём появления qt_object из QWebChannel
    function waitForBridge() {
        try {
            if (typeof qt_object !== 'undefined' && typeof qt_object.onPreviewScroll === 'function') {
                bridge = qt_object;
                startPolling();
            } else {
                setTimeout(waitForBridge, 50);
            }
        } catch(e) {
            setTimeout(waitForBridge, 50);
        }
    }

    // Запускаем ожидание
    waitForBridge();
})();
"""

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
    var anchor = '{md_anchor}';
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
            base_dir=get_base_dir(),
        )

    def toggle_theme(self) -> None:
        """Для совместимости: переключить тему предпросмотра."""
        self._toggle_theme()
