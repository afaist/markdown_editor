"""Файловые операции: открытие, сохранение, экспорт."""

import os
import tempfile
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QUrl, QTimer

from markdown_editor_pkg.markdown_renderer import MarkdownRenderer


class FileOperations:
    """Управление файлами: открытие, сохранение, экспорт в HTML/PDF."""

    def __init__(self, editor, statusbar, renderer: MarkdownRenderer):
        self.editor = editor
        self.statusbar = statusbar
        self.renderer = renderer

    # ─── Открытие / Сохранение ───────────────────────────────────────────

    def open_file(self) -> None:
        """Открыть Markdown-файл через диалог."""
        filepath, _ = QFileDialog.getOpenFileName(
            self.editor,
            "Открыть файл",
            "",
            "Markdown files (*.md);;Text files (*.txt);;All files (*)",
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor._set_editor_text_without_dirty(content)
            self.editor.current_file = filepath
            self.editor.is_dirty = False
            self.editor.update_preview()
            self.editor.update_char_count()
            self.statusbar.showMessage(f"Файл открыт: {filepath}")
            self.editor.save_last_session(filepath)
        except Exception as e:
            QMessageBox.critical(self.editor, "Ошибка", f"Не удалось открыть файл:\n{str(e)}")

    def save_file(self) -> None:
        """Сохранить текущий файл (или вызвать save_file_as, если путь не задан)."""
        if not self.editor.current_file:
            self.save_file_as()
            return

        try:
            content = self.editor.editor.toPlainText()
            with open(self.editor.current_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.editor.is_dirty = False
            self.statusbar.showMessage(f"Файл сохранен: {self.editor.current_file}")
        except Exception as e:
            QMessageBox.critical(self.editor, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def save_file_as(self) -> None:
        """Сохранить файл под новым именем."""
        filepath, _ = QFileDialog.getSaveFileName(
            self.editor,
            "Сохранить как...",
            "",
            "Markdown files (*.md);;Text files (*.txt);;All files (*)",
        )
        if filepath:
            self.editor.current_file = filepath
            self.save_file()

    def new_file(self) -> None:
        """Создать новый файл, предложив сохранить текущий при наличии изменений."""
        if self.editor.is_dirty:
            result = QMessageBox.question(
                self.editor,
                "Сохранить?",
                "Сохранить текущий файл?",
            )
            if result == QMessageBox.StandardButton.Yes:
                self.save_file()
                if self.editor.current_file is None:
                    return
            elif result == QMessageBox.StandardButton.Cancel:
                return

        self.editor._set_editor_text_without_dirty("")
        self.editor.current_file = None
        self.editor.is_dirty = False
        self.editor.update_preview()
        self.statusbar.showMessage("Новый файл создан")

    # ─── Экспорт ─────────────────────────────────────────────────────────

    def _get_pdf_headers(self) -> dict:
        """Возвращает настройки колонтитулов для PDF-экспорта."""
        filename = self.editor.current_file or ""
        doc_title = "Markdown Editor"
        if filename:
            doc_title = os.path.basename(filename)

        return {
            "show_headers": True,
            "header_text": doc_title,
            "footer_text": "markdown_editor",
        }

    def export_to_html(self) -> None:
        """Экспортировать Markdown в HTML-файл."""
        filepath, _ = QFileDialog.getSaveFileName(
            self.editor, "Экспорт в HTML", "", "HTML files (*.html);;All files (*)"
        )
        if not filepath:
            return

        try:
            html = self.renderer.render(
                self.editor.editor.toPlainText(),
                theme_name=self.editor.theme_manager.theme_name,
                base_dir=os.path.dirname(__file__),
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            self.statusbar.showMessage(f"Экспорт в HTML завершен: {filepath}")
        except Exception as e:
            QMessageBox.critical(
                self.editor, "Ошибка", f"Не удалось экспортировать в HTML:\n{str(e)}"
            )

    def export_to_pdf(self) -> None:
        """Экспортировать Markdown в PDF через QWebEngineView."""
        filepath, _ = QFileDialog.getSaveFileName(
            self.editor, "Экспорт в PDF", "", "PDF files (*.pdf);;All files (*)"
        )
        if not filepath:
            return

        if not filepath.lower().endswith(".pdf"):
            filepath += ".pdf"

        self.statusbar.showMessage("Экспорт в PDF... Генерация PDF")

        try:
            # Создаём временный HTML-файл
            tmp_path = None
            with tempfile.NamedTemporaryFile(
                suffix=".html", delete=False, mode="w", encoding="utf-8"
            ) as tmp:
                headers = self._get_pdf_headers()
                html_content = self.renderer.render(
                    self.editor.editor.toPlainText(),
                    theme_name=self.editor.theme_manager.theme_name,
                    base_dir=os.path.dirname(__file__),
                    headers=headers,
                )
                tmp.write(html_content)
                tmp_path = tmp.name

            self.editor.preview.setUrl(QUrl.fromLocalFile(tmp_path))

            def on_load_finished(ok: bool) -> None:
                if not ok:
                    QMessageBox.critical(
                        self.editor, "Ошибка", "Не удалось загрузить HTML для экспорта."
                    )
                    self.statusbar.showMessage("")
                    self._cleanup_temp_file(tmp_path)
                    return

                try:
                    self.editor.preview.page().loadFinished.disconnect(on_load_finished)
                except TypeError:
                    pass

                page = self.editor.preview.page()
                if page is None:
                    QMessageBox.critical(
                        self.editor, "Ошибка", "Страница предпросмотра не инициализирована."
                    )
                    self.statusbar.showMessage("")
                    self._cleanup_temp_file(tmp_path)
                    return

                def attempt_pdf_write() -> None:
                    try:
                        def callback(pdf_data) -> None:
                            try:
                                with open(filepath, "wb") as f:
                                    f.write(bytes(pdf_data))
                                self.statusbar.showMessage(
                                    f"Экспорт в PDF завершен: {filepath}"
                                )
                            except Exception as e:
                                QMessageBox.critical(
                                    self.editor,
                                    "Ошибка",
                                    f"Не удалось записать PDF файл: {str(e)}",
                                )
                                self.statusbar.showMessage("")
                            finally:
                                self._cleanup_temp_file(tmp_path)

                        page.printToPdf(callback)
                    except Exception as e:
                        QMessageBox.critical(
                            self.editor, "Ошибка", f"Ошибка печати: {str(e)}"
                        )
                        self.statusbar.showMessage("")
                        self._cleanup_temp_file(tmp_path)

                QTimer.singleShot(500, attempt_pdf_write)

            self.editor.preview.page().loadFinished.connect(on_load_finished)

        except Exception as e:
            QMessageBox.critical(
                self.editor, "Ошибка", f"Не удалось начать экспорт в PDF:\n{str(e)}"
            )
            self.statusbar.showMessage("")
            if tmp_path and os.path.exists(tmp_path):
                self._cleanup_temp_file(tmp_path)

    @staticmethod
    def _cleanup_temp_file(path: str | None) -> None:
        """Удаляет временный файл."""
        try:
            if path and os.path.exists(path):
                os.unlink(path)
        except Exception:
            pass
