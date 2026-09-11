"""Event handlers — editor event processing."""

import os
from typing import TYPE_CHECKING

from PyQt6.QtCore import QUrl

from markdown_editor_pkg.i18n import tr
from markdown_editor_pkg.resource_path import get_base_dir

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class EventHandler:
    """Обработчики событий: textChanged, обновление предпросмотра, статус."""

    def __init__(self, editor: "MarkdownEditorPyQt"):
        """Инициализация обработчика событий.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
        """
        self.editor = editor
        # Флаг для предотвращения рекурсии при синхронизации скролла
        self._syncing_scroll = False
        # Флаг: True если скролл инициирован из превью (нужно скроллить редактор)
        self._scroll_from_preview = False
        # Флаг: True если скролл инициирован из редактора (нужно скроллить превью)
        self._scroll_from_editor = False

    def connect(self) -> None:
        """Подключить обработчики к сигналам (вызывается после init_ui).

        Примечание: сигналы textChanged уже подключены в UIBuilder,
        поэтому этот метод в настоящее время пуст.
        """
        # Сигналы уже подключены в UIBuilder, здесь нет нужды

    def on_text_change(self) -> None:
        """Обработка изменения текста."""
        text = self.editor.editor.toPlainText()
        self.editor.is_dirty = bool(text.strip())
        self.editor.update_char_count()

        if self.editor.current_file and self.editor.is_dirty:
            self.editor.auto_save_timer.start(3000)

        self.editor.preview_timer.stop()
        self.editor.preview_timer.start(300)

    def update_file_status(self) -> None:
        """Обновить отображение имени файла в строке состояния."""
        if not self.editor.file_name_label:
            return

        if self.editor.current_file:
            filename = os.path.basename(self.editor.current_file)
            if self.editor.is_dirty:
                self.editor.file_name_label.setText(
                    tr("Unsaved file. {filename}").format(filename=filename)
                )
                self.editor.file_name_label.setStyleSheet("color: #cc6600; font-weight: bold;")
            else:
                self.editor.file_name_label.setText(filename)
                self.editor.file_name_label.setStyleSheet("color: #333333; font-weight: normal;")
        else:
            if self.editor.is_dirty:
                self.editor.file_name_label.setText(tr("Unsaved file. Name not set."))
                self.editor.file_name_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            else:
                self.editor.file_name_label.setText("")
                self.editor.file_name_label.setStyleSheet("color: #333333; font-weight: normal;")

    def update_preview(self) -> None:
        """Обновить предпросмотр."""
        markdown_text = self.editor.editor.toPlainText()
        base_dir = get_base_dir()
        html = self.editor.renderer.render(
            markdown_text,
            theme_name=self.editor.theme_manager.theme_name,
            base_dir=base_dir,
        )
        base_url = QUrl.fromLocalFile(base_dir or ".")
        self.editor.preview.setHtml(html, base_url)
        # После обновления превью — синхронизируем прокрутку к курсору
        self.editor._scroll_preview_to_cursor()
        # Перезапускаем JS-трекер скролла
        self.editor.scroll_sync._init_scroll_tracker(delay=50)
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(tr("Preview updated"))

    def update_char_count(self) -> None:
        """Обновить счётчики символов и слов."""
        text = self.editor.editor.toPlainText()
        if self.editor._statusbar_ref:
            char_lbl = self.editor.char_count_label
            word_lbl = self.editor.word_count_label
            if char_lbl is not None:
                char_lbl.setText(tr("Characters: {count}").format(count=len(text)))
            if word_lbl is not None:
                word_lbl.setText(tr("Words: {count}").format(count=len(text.split())))

    def on_cursor_position_changed(self) -> None:
        """Синхронизация предпросмотра с позицией курсора в редакторе.

        Прокрутка превью выполняется в update_preview после обновления HTML,
        чтобы ID заголовков уже были доступны в DOM.
        """

    def set_editor_text_without_dirty(self, text: str) -> None:
        """Установка текста без is_dirty."""
        self.editor.editor.blockSignals(True)
        self.editor.editor.setPlainText(text)
        self.editor.editor.blockSignals(False)

    # ─── Синхронизация прокрутки ──────────────────────────────────────────

    def sync_scroll_from_editor(self) -> None:
        """Синхронизация прокрутки превью при скролле редактора."""
        if self._syncing_scroll or self._scroll_from_preview:
            return

        editor = self.editor.editor
        preview = self.editor.preview

        if not editor or not preview:
            return

        try:
            self._syncing_scroll = True
            self._scroll_from_preview = False
            self._scroll_from_editor = True

            vbar = editor.verticalScrollBar()
            if vbar is None:
                return

            slider_pos = vbar.value()
            slider_max = vbar.maximum()
            slider_min = vbar.minimum()

            if slider_max == slider_min:
                scroll_pct = 0.0
            else:
                scroll_pct = slider_pos / (slider_max - slider_min)

            # Устанавливаем флаг в JS, чтобы предотвратить отправку события обратно
            js_set = "try { qt_object._isScrolling = true; setTimeout(function(){ qt_object._isScrolling = false; }, 100); } catch(e) {}"
            preview_page = preview.page()
            if preview_page is not None:
                preview_page.runJavaScript(js_set)

            # QWebEngineView не имеет прямого API для скроллбара, используем JS
            js = f"window.scrollTo(0, {scroll_pct} * (document.documentElement.scrollHeight - window.innerHeight));"
            if preview_page is not None:
                preview_page.runJavaScript(js)
        finally:
            self._syncing_scroll = False
            self._scroll_from_editor = False

    def sync_scroll_from_preview(self, scroll_pct: float) -> None:
        """Синхронизация прокрутки редактора при скролле превью.

        Args:
            scroll_pct: Пропорция прокрутки превью (0.0 — верх, 1.0 — низ)
        """
        if self._syncing_scroll or not self._scroll_from_preview:
            return

        editor = self.editor.editor
        if not editor:
            return

        try:
            self._syncing_scroll = True

            vbar = editor.verticalScrollBar()
            if vbar is None:
                return

            slider_max = vbar.maximum()
            slider_min = vbar.minimum()

            if slider_max == slider_min:
                return

            new_pos = int(scroll_pct * (slider_max - slider_min))
            new_pos = max(slider_min, min(slider_max, new_pos))
            vbar.setValue(new_pos)
        finally:
            self._syncing_scroll = False

    def on_preview_scroll(self, scroll_pct: float) -> None:
        """Обработчик скролла превью (вызывается из JavaScript).

        Args:
            scroll_pct: Пропорция прокрутки (0.0 — верх, 1.0 — низ)
        """
        self._scroll_from_preview = True
        self.sync_scroll_from_preview(scroll_pct)
        self._scroll_from_preview = False
