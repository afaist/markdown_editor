"""Event handlers — обработчики событий редактора."""

import os
from typing import TYPE_CHECKING

from PyQt6.QtCore import QUrl

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class EventHandler:    
    """Обработчики событий: textChanged, обновление предпросмотра, статус."""
    
    def __init__(self, editor: "MarkdownEditorPyQt"):
        self.editor = editor

    def connect(self) -> None:
        """Подключить обработчики к сигналам (вызывается после init_ui)."""
        # Сигналы уже подключены в UIBuilder, здесь нет нужды
        pass

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
                self.editor.file_name_label.setText(f"Файл не сохранён. {filename}")
                self.editor.file_name_label.setStyleSheet("color: #cc6600; font-weight: bold;")
            else:
                self.editor.file_name_label.setText(filename)
                self.editor.file_name_label.setStyleSheet("color: #333333; font-weight: normal;")
        else:
            if self.editor.is_dirty:
                self.editor.file_name_label.setText("Файл не сохранён. Имя не задано.")
                self.editor.file_name_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            else:
                self.editor.file_name_label.setText("")
                self.editor.file_name_label.setStyleSheet("color: #333333; font-weight: normal;")

    def update_preview(self) -> None:
        """Обновить предпросмотр."""
        markdown_text = self.editor.editor.toPlainText()
        html = self.editor.renderer.render(
            markdown_text,
            theme_name=self.editor.theme_manager.theme_name,
            base_dir=os.path.dirname(os.path.abspath(__file__)),
            )
        base_dir = os.path.dirname(os.path.abspath(__file__))
        base_url = QUrl.fromLocalFile(base_dir or ".")
        self.editor.preview.setHtml(html, base_url)
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage("Предпросмотр обновлён")

    def update_char_count(self) -> None:
        """Обновить счётчики символов и слов."""
        text = self.editor.editor.toPlainText()
        if self.editor._statusbar_ref:
            char_lbl = self.editor.char_count_label
            word_lbl = self.editor.word_count_label
            if char_lbl is not None:
                char_lbl.setText(f"Символов: {len(text)}")
            if word_lbl is not None:
                word_lbl.setText(f"Слов: {len(text.split())}")

    def on_cursor_position_changed(self) -> None:
        """Синхронизация предпросмотра с позицией курсора в редакторе."""
        self.editor._scroll_preview_to_cursor()

    def set_editor_text_without_dirty(self, text: str) -> None:
        """Установка текста без is_dirty."""
        self.editor.editor.blockSignals(True)
        self.editor.editor.setPlainText(text)
        self.editor.editor.blockSignals(False)
