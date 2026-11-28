"""Файловые операции: открытие, сохранение, экспорт."""

from __future__ import annotations

import base64
import logging
import os
import re
import tempfile
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from markdown_editor_pkg.markdown_renderer import MarkdownRenderer
from markdown_editor_pkg.resource_path import get_base_dir


@dataclass
class EditorState:
    """Контекст состояния редактора: текущий файл и чистота.

    Attributes:
        current_file: Путь к текущему открытому файлу или None.
        is_dirty: Флаг наличия несохранённых изменений.
    """

    current_file: str | None = None
    is_dirty: bool = False

    def mark_clean(self) -> None:
        """Установить флаг is_dirty в False."""
        self.is_dirty = False

    def mark_dirty(self) -> None:
        """Установить флаг is_dirty в True."""
        self.is_dirty = True


class FileIO:
    """Открытие, сохранение, новые файлы."""

    def __init__(
        self,
        editor,
        statusbar,
        renderer: MarkdownRenderer,
        state: EditorState,
        recent_files=None,
    ):
        """Инициализация обработчика файловых операций.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
            statusbar: Ссылка на QStatusBar для сообщений.
            renderer: Экземпляр MarkdownRenderer для рендеринга.
            state: Экземпляр EditorState для управления состоянием.
            recent_files: Экземпляр RecentFilesManager для отслеживания открытых файлов.
        """
        self._editor = editor
        self._statusbar = statusbar
        self._renderer = renderer
        self._state = state
        self._recent_files = recent_files

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
        logger.info("Opening file: %s", filepath)
        try:
            content = self._read_file(filepath)
            logger.debug("File read successfully: %d chars", len(content))
        except Exception:
            logger.exception("Failed to read file: %s", filepath)
            raise

        self._editor._set_editor_text_without_dirty(content)
        self._state.current_file = filepath
        self._state.mark_clean()
        self._editor.update_preview()
        self._editor.update_char_count()
        self._editor.update_validation()
        self._editor.update_file_status()
        self._status_msg(f"Файл открыт: {filepath}")
        self._editor.save_last_session(filepath)
        if self._recent_files is not None:
            self._recent_files.add(filepath)

    # ─── Открытие / Сохранение ─────────────────────────────────────────

    def open_file(self) -> None:
        """Открыть Markdown-файл через диалог выбора файла.

        Показывает QFileDialog, читает содержимое, обновляет редактор,
        статус и предпросмотр.
        """
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
        except Exception:
            logger.exception("Failed to open file: %s", filepath)
            self._error_msg("Ошибка", f"Не удалось открыть файл:\n{filepath}")

    def save_file(self) -> None:
        """Сохранить текущий файл в _state.current_file.

        Если путь не задан, вызывает save_file_as. Записывает содержимое
        редактора в файл и сбрасывает флаг is_dirty.
        """
        if not self._state.current_file:
            self.save_file_as()
            return

        try:
            content = self._editor.editor.toPlainText()
            self._write_file(self._state.current_file, content)
            self._state.mark_clean()
            self._editor.update_file_status()
            self._status_msg(f"Файл сохранен: {self._state.current_file}")
            logger.info("File saved: %s (%d chars)", self._state.current_file, len(content))
        except Exception:
            logger.exception("Failed to save file: %s", self._state.current_file)
            self._error_msg("Ошибка", f"Не удалось сохранить файл:\n{self._state.current_file}")

    def save_file_as(self) -> None:
        """Сохранить файл под новым именем через диалог QFileDialog.

        Устанавливает новый путь в _state.current_file и вызывает save_file().
        Автоматически добавляет расширение .md, если оно не указано.
        """
        filepath, _ = QFileDialog.getSaveFileName(
            self._editor,
            "Сохранить как...",
            "",
            "Markdown files (*.md);;Text files (*.txt);;All files (*)",
        )
        if filepath:
            if not filepath.lower().endswith(".md"):
                filepath += ".md"
            self._state.current_file = filepath
            self.save_file()

    def new_file(self) -> None:
        """Создать новый файл, предложив сохранить текущий при наличии изменений.

        Если есть несохранённые изменения, показывает QMessageBox с вопросом
        о сохранении. Очищает редактор и сбрасывает состояние.
        """
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
        # Очистить last_file в конфиге — нового файла пока нет
        from markdown_editor_pkg.session_manager import SessionManager

        SessionManager.save("")
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
        """Инициализация обработчика экспорта.

        Args:
            editor: Ссылка на основной объект MarkdownEditorPyQt.
            statusbar: Ссылка на QStatusBar для сообщений.
            renderer: Экземпляр MarkdownRenderer для рендеринга.
            state: Экземпляр EditorState для управления состоянием.
        """
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

        return {
            "show_headers": False,
            "header_text": "",
            "footer_text": "",
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
            logger.info("Exporting to HTML: %s", filepath)
            html = self._renderer.render(
                self._editor.editor.toPlainText(),
                theme_name=self._editor.theme_manager.theme_name,
                base_dir=get_base_dir(),
            )
            self._write_file(filepath, html)
            self._status_msg(f"Экспорт в HTML завершен: {filepath}")
            logger.info("HTML export completed: %s (%d bytes)", filepath, len(html))
        except Exception:
            logger.exception("Failed to export HTML: %s", filepath)
            self._error_msg("Ошибка", f"Не удалось экспортировать в HTML:\n{filepath}")

    def export_to_pdf(self) -> None:
        """Экспортировать Markdown в PDF через QWebEngineView.

        Генерирует временный HTML-файл, загружает его в preview и вызывает
        page.printToPdf() для записи PDF в выбранный файл.
        """
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
            base_dir=get_base_dir(),
            headers=headers,
        )

        # Встраиваем изображения как data URI — file:// не работает из temp-файла
        current_file = self._editor.current_file
        file_dir = ""
        if current_file:
            file_dir = os.path.dirname(os.path.abspath(current_file))

        html_content = self._embed_images(html_content, file_dir)

        tmp_path: str | None = None
        with tempfile.NamedTemporaryFile(
            suffix=".html", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        return tmp_path  # type: ignore[return-value]

    @staticmethod
    def _embed_images(html: str, file_dir: str) -> str:
        """Заменить src у <img> на data URI для корректного отображения в PDF."""

        def replace_img_src(match: re.Match) -> str:
            full_tag: str = match.group(0)
            src_match = re.search(r'src=["\']([^"\']*)["\']', full_tag)
            if not src_match:
                return full_tag

            src = src_match.group(1)
            # Пропускаем http(s), data:, и другие внешние URL
            if src.startswith(("http://", "https://", "data:", "mailto:")):
                return full_tag

            # Определяем MIME-тип по расширению
            ext = os.path.splitext(src)[1].lower()
            mime_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".svg": "image/svg+xml",
                ".bmp": "image/bmp",
            }
            mime_type = mime_map.get(ext, "image/png")

            # Разрешаем путь относительно директории markdown-файла
            if not os.path.isabs(src):
                resolved = os.path.normpath(os.path.join(file_dir, src))
            else:
                resolved = src

            # Читаем файл и конвертируем в base64
            try:
                with open(resolved, "rb") as f:
                    data = base64.b64encode(f.read()).decode("ascii")
                return full_tag.replace(src, f"data:{mime_type};base64,{data}", 1)
            except OSError:
                return full_tag

        return re.sub(r"<img[^>]+>", replace_img_src, html)

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
