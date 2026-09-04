"""Файловые операции: открытие, сохранение, экспорт."""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from markdown_editor_pkg.markdown_renderer import MarkdownRenderer


@dataclass
class EditorState:
    """Контекст состояния редактора: текущий файл и чистота."""

    current_file: str | None = None
    is_dirty: bool = False

    def mark_clean(self) -> None:
        self.is_dirty = False

    def mark_dirty(self) -> None:
        self.is_dirty = True


class FileIO:
    """Открытие, сохранение, новые файлы."""

    def __init__(
        self,
        editor,
        statusbar,
        renderer: MarkdownRenderer,
        state: EditorState,
    ):
        self._editor = editor
        self._statusbar = statusbar
        self._renderer = renderer
        self._state = state

    # ─── Вспомогательные методы ─────────────────────────────────────────

    def _status_msg(self, msg: str) -> None:
        if self._statusbar:
            self._statusbar.showMessage(msg)

    def _error_msg(self, title: str, message: str) -> None:
        QMessageBox.critical(self._editor, title, message)

    def _read_file(self, path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    def _write_file(self, path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _on_file_opened(self, filepath: str) -> None:
        """Общий хук после успешного открытия файла."""
        content = self._read_file(filepath)
        self._editor._set_editor_text_without_dirty(content)
        self._state.current_file = filepath
        self._state.mark_clean()
        self._editor.update_preview()
        self._editor.update_char_count()
        self._editor.update_file_status()
        self._status_msg(f"Файл открыт: {filepath}")
        self._editor.save_last_session(filepath)

    # ─── Открытие / Сохранение ─────────────────────────────────────────

    def open_file(self) -> None:
        """Открыть Markdown-файл через диалог."""
        filepath, _ = QFileDialog.getOpenFileName(
            self._editor,
            "Открыть файл",
            "",
            "Markdown files (*.md);;Text files (*.txt);;All files (*)",
        )
        if not filepath:
            return

        try:
            self._on_file_opened(filepath)
        except Exception as e:
            self._error_msg("Ошибка", f"Не удалось открыть файл:\n{e!s}")

    def save_file(self) -> None:
        """Сохранить текущий файл (или вызвать save_file_as, если путь не задан)."""
        if not self._state.current_file:
            self.save_file_as()
            return

        try:
            content = self._editor.editor.toPlainText()
            self._write_file(self._state.current_file, content)
            self._state.mark_clean()
            self._editor.update_file_status()
            self._status_msg(f"Файл сохранен: {self._state.current_file}")
        except Exception as e:
            self._error_msg("Ошибка", f"Не удалось сохранить файл:\n{e!s}")

    def save_file_as(self) -> None:
        """Сохранить файл под новым именем."""
        filepath, _ = QFileDialog.getSaveFileName(
            self._editor,
            "Сохранить как...",
            "",
            "Markdown files (*.md);;Text files (*.txt);;All files (*)",
        )
        if filepath:
            self._state.current_file = filepath
            self.save_file()

    def new_file(self) -> None:
        """Создать новый файл, предложив сохранить текущий при наличии изменений."""
        if self._state.is_dirty:
            result = QMessageBox.question(
                self._editor,
                "Сохранить?",
                "Сохранить текущий файл?",
            )
            if result == QMessageBox.StandardButton.Yes:
                self.save_file()
                if self._state.current_file is None:
                    return
            elif result == QMessageBox.StandardButton.Cancel:
                return

        self._editor._set_editor_text_without_dirty("")
        self._state.current_file = None
        self._state.mark_clean()
        self._editor.update_preview()
        self._editor.update_file_status()
        self._status_msg("Новый файл создан")


class FileExport:
    """Экспорт в HTML, PDF."""

    def __init__(
        self,
        editor,
        statusbar,
        renderer: MarkdownRenderer,
        state: EditorState,
    ):
        self._editor = editor
        self._statusbar = statusbar
        self._renderer = renderer
        self._state = state
        # Настройки колонтитулов PDF (None = использовать значения по умолчанию)
        self._pdf_headers: dict | None = None

    def set_pdf_headers(self, headers: dict) -> None:
        """Установить пользовательские настройки колонтитулов PDF."""
        self._pdf_headers = headers

    # ─── Вспомогательные методы ─────────────────────────────────────────

    def _status_msg(self, msg: str) -> None:
        if self._statusbar:
            self._statusbar.showMessage(msg)

    def _error_msg(self, title: str, message: str) -> None:
        QMessageBox.critical(self._editor, title, message)

    def _write_file(self, path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _get_pdf_headers(self) -> dict:
        """Возвращает настройки колонтитулов для PDF-экспорта."""
        if self._pdf_headers is not None:
            return self._pdf_headers

        filename = self._state.current_file or ""
        doc_title = "Markdown Editor"
        if filename:
            doc_title = os.path.basename(filename)

        return {
            "show_headers": True,
            "header_text": doc_title,
            "footer_text": "markdown_editor  —  ",
        }

    # ─── Экспорт ────────────────────────────────────────────────────────

    def export_to_html(self) -> None:
        """Экспортировать Markdown в HTML-файл."""
        filepath, _ = QFileDialog.getSaveFileName(
            self._editor, "Экспорт в HTML", "", "HTML files (*.html);;All files (*)"
        )
        if not filepath:
            return

        if not filepath.lower().endswith(".html"):
            filepath += ".html"

        try:
            html = self._renderer.render(
                self._editor.editor.toPlainText(),
                theme_name=self._editor.theme_manager.theme_name,
                base_dir=os.path.dirname(__file__),
            )
            self._write_file(filepath, html)
            self._status_msg(f"Экспорт в HTML завершен: {filepath}")
        except Exception as e:
            self._error_msg("Ошибка", f"Не удалось экспортировать в HTML:\n{e!s}")

    def export_to_pdf(self) -> None:
        """Экспортировать Markdown в PDF через QWebEngineView."""
        filepath, _ = QFileDialog.getSaveFileName(
            self._editor, "Экспорт в PDF", "", "PDF files (*.pdf);;All files (*)"
        )
        if not filepath:
            return

        if not filepath.lower().endswith(".pdf"):
            filepath += ".pdf"

        self._status_msg("Экспорт в PDF... Генерация PDF")

        try:
            tmp_path = self._write_temp_html()
            self._editor.preview.setUrl(QUrl.fromLocalFile(tmp_path))

            def on_load_finished(ok: bool) -> None:
                if not ok:
                    self._error_msg("Ошибка", "Не удалось загрузить HTML для экспорта.")
                    self._status_msg("")
                    self._cleanup_temp_file(tmp_path)
                    return

                try:
                    self._editor.preview.page().loadFinished.disconnect(on_load_finished)
                except TypeError:
                    pass

                page = self._editor.preview.page()
                if page is None:
                    self._error_msg("Ошибка", "Страница предпросмотра не инициализирована.")
                    self._status_msg("")
                    self._cleanup_temp_file(tmp_path)
                    return

                QTimer.singleShot(500, lambda: self._do_pdf_write(page, filepath, tmp_path))

            self._editor.preview.page().loadFinished.connect(on_load_finished)

        except Exception as e:
            self._error_msg("Ошибка", f"Не удалось начать экспорт в PDF:\n{e!s}")
            self._status_msg("")
            if "tmp_path" in locals() and tmp_path and os.path.exists(tmp_path):
                self._cleanup_temp_file(tmp_path)

    def _write_temp_html(self) -> str:
        """Создаёт временный HTML-файл и возвращает его путь."""
        headers = self._get_pdf_headers()
        html_content = self._renderer.render(
            self._editor.editor.toPlainText(),
            theme_name=self._editor.theme_manager.theme_name,
            base_dir=os.path.dirname(__file__),
            headers=headers,
        )

        tmp_path: str | None = None
        with tempfile.NamedTemporaryFile(
            suffix=".html", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        return tmp_path  # type: ignore[return-value]

    def _do_pdf_write(self, page, filepath: str, tmp_path: str) -> None:
        """Выполняет запись PDF из страницы."""
        try:

            def callback(pdf_data) -> None:
                try:
                    with open(filepath, "wb") as f:
                        f.write(bytes(pdf_data))
                    self._status_msg(f"Экспорт в PDF завершен: {filepath}")
                except Exception as e:
                    self._error_msg("Ошибка", f"Не удалось записать PDF файл: {e!s}")
                    self._status_msg("")
                finally:
                    self._cleanup_temp_file(tmp_path)

            page.printToPdf(callback)
        except Exception as e:
            self._error_msg("Ошибка", f"Ошибка печати: {e!s}")
            self._status_msg("")
            self._cleanup_temp_file(tmp_path)

    @staticmethod
    def _cleanup_temp_file(path: str | None) -> None:
        """Удаляет временный файл."""
        try:
            if path and os.path.exists(path):
                os.unlink(path)
        except OSError:
            logger.exception("Failed to cleanup temp file: %s", path)
