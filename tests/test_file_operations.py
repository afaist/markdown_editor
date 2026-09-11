"""Tests for PDF headers in FileOperations."""

from unittest import mock

from markdown_editor_pkg.editor import MarkdownEditorPyQt


class TestFileOperationsHeaders:
    """Тесты колонтитулов в FileOperations."""

    def setup_method(self):
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def teardown_method(self):
        self.editor.close()

    def test_get_pdf_headers_no_file(self):
        """Колонтитулы без открытого файла используют default название."""
        self.editor.current_file = None
        headers = self.editor.file_export._get_pdf_headers()
        assert headers["show_headers"] is True
        assert headers["header_text"] == "Markdown Editor"
        assert "markdown_editor" in headers["footer_text"]
        assert "—" in headers["footer_text"]

    def test_get_pdf_headers_with_file(self):
        """Колонтитулы с открытым файлом используют имя файла."""
        self.editor.current_file = "/home/user/my_document.md"
        headers = self.editor.file_export._get_pdf_headers()
        assert headers["show_headers"] is True
        assert headers["header_text"] == "my_document.md"
        assert "—" in headers["footer_text"]


class TestFileOperationsIO:
    """Тесты файловых операций (IO)."""

    def setup_method(self):
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def teardown_method(self):
        self.editor.close()

    def test_save_file_no_path_calls_save_as(self):
        """save_file без пути должен вызвать save_file_as."""
        self.editor.current_file = None
        self.editor.editor.setPlainText("тест")

        # Patch QFileDialog in the file_operations module where it is used
        with mock.patch("markdown_editor_pkg.file_operations.QFileDialog") as mock_qfile_dialog:
            mock_qfile_dialog.getSaveFileName.return_value = ("/tmp/test.md", "")
            self.editor.file_ops.save_file()

        assert self.editor.current_file == "/tmp/test.md"

    def test_save_file_as(self):
        """save_file_as сохраняет файл под новым именем."""
        self.editor.current_file = None
        self.editor.editor.setPlainText("содержимое файла")

        # Patch QFileDialog in the file_operations module where it is used
        with mock.patch("markdown_editor_pkg.file_operations.QFileDialog") as mock_qfile_dialog:
            mock_qfile_dialog.getSaveFileName.return_value = ("/tmp/new_file.md", "")
            self.editor.file_ops.save_file_as()

        assert self.editor.current_file == "/tmp/new_file.md"
        assert self.editor.is_dirty is False

    def test_new_file_no_changes(self):
        """new_file без изменений не показывает диалог."""
        self.editor.current_file = None
        self.editor.is_dirty = False
        self.editor.editor.setPlainText("")

        # Patch QMessageBox and QFileDialog in the file_operations module
        with (
            mock.patch("markdown_editor_pkg.file_operations.QMessageBox") as mock_qmsg_box,
            mock.patch("markdown_editor_pkg.file_operations.QFileDialog") as mock_qfile_dialog,
        ):
            mock_qfile_dialog.getSaveFileName.return_value = ("/tmp/new.md", "")

            self.editor.file_ops.new_file()

        mock_qmsg_box.question.assert_not_called()
        assert self.editor.current_file is None
        assert self.editor.editor.toPlainText() == ""

    def test_new_file_with_changes_shows_dialog(self):
        """new_file с изменениями показывает диалог сохранения."""
        self.editor.current_file = "/tmp/existing.md"
        self.editor.is_dirty = True
        self.editor.editor.setPlainText("есть изменения")

        # Используем mock.patch для патчинга QMessageBox в модуле file_operations
        with mock.patch("markdown_editor_pkg.file_operations.QMessageBox") as mock_qmsg_box:
            # Устанавливаем возвращаемое значение для метода question
            mock_qmsg_box.question.return_value = mock_qmsg_box.StandardButton.No
            self.editor.file_ops.new_file()

        mock_qmsg_box.question.assert_called_once()
        assert self.editor.current_file is None
        assert self.editor.editor.toPlainText() == ""

    def test_new_file_with_changes_save_yes(self):
        """new_file с изменениями — пользователь нажал 'Да'."""
        import tempfile

        # Создаем временный файл для хранения результатов сохранения
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_path = temp_file.name

        self.editor.current_file = temp_path
        self.editor.is_dirty = True
        self.editor.editor.setPlainText("важный текст")

        # Используем mock.patch для патчинга QMessageBox и QFileDialog в модуле file_operations
        with (
            mock.patch("markdown_editor_pkg.file_operations.QMessageBox") as mock_qmsg_box,
            mock.patch("markdown_editor_pkg.file_operations.QFileDialog") as mock_qfile_dialog,
        ):
            # Если save_file_as вызывается (например, если current_file был None),
            # нужно вернуть путь. Но в данном тесте current_file есть.
            # Однако, если логика new_file сначала сбрасывает current_file в None,
            # то save_file вызовет save_file_as.
            # Чтобы быть уверенными, патчим QFileDialog.
            mock_qfile_dialog.getSaveFileName.return_value = (temp_path, "")

            mock_qmsg_box.question.return_value = mock_qmsg_box.StandardButton.Yes
            self.editor.file_ops.new_file()

        assert (
            self.editor.current_file is None
        )  # После new_file текущий файл должен стать None (или новым)
        assert self.editor.editor.toPlainText() == ""

    def test_new_file_with_changes_cancel(self):
        """new_file с изменениями — пользователь нажал 'Отмена'."""
        self.editor.current_file = "/tmp/test.md"
        self.editor.is_dirty = True
        self.editor.editor.setPlainText("важный текст")

        # Используем mock.patch для патчинга QMessageBox в модуле file_operations
        with mock.patch("markdown_editor_pkg.file_operations.QMessageBox") as mock_qmsg_box:
            # Устанавливаем возвращаемое значение для метода question
            mock_qmsg_box.question.return_value = mock_qmsg_box.StandardButton.Cancel
            self.editor.file_ops.new_file()

        # Файл не должен быть изменён
        assert self.editor.current_file == "/tmp/test.md"
        assert self.editor.editor.toPlainText() == "важный текст"
        self.editor.editor.setPlainText("")


class TestFileOperationsExport:
    """Тесты экспорта (FileExport)."""

    def setup_method(self):
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def teardown_method(self):
        self.editor.is_dirty = False
        self.editor.close()

    def test_export_to_html(self):
        """Экспорт в HTML записывает файл с HTML-контентом."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
            temp_path = temp_file.name

        self.editor.editor.setPlainText("# Hello World")

        with mock.patch("markdown_editor_pkg.file_operations.QFileDialog") as mock_qfile_dialog:
            mock_qfile_dialog.getSaveFileName.return_value = (temp_path, "")
            self.editor.file_export.export_to_html()

        assert os.path.exists(temp_path)
        with open(temp_path) as f:
            content = f.read()
            assert "<h1" in content
            assert "Hello World" in content
            os.unlink(temp_path)

    def test_export_to_html_adds_extension(self):
        """Экспорт в HTML добавляет .html, если пользователь не указал расширение."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix="", delete=False) as temp_file:
            temp_path = temp_file.name

        self.editor.editor.setPlainText("# Test")

        with mock.patch("markdown_editor_pkg.file_operations.QFileDialog") as mock_qfile_dialog:
            mock_qfile_dialog.getSaveFileName.return_value = (temp_path, "")
            self.editor.file_export.export_to_html()

        # Файл должен быть создан с .html расширением
        expected_path = temp_path + ".html"
        assert os.path.exists(expected_path)
        os.unlink(expected_path)
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_set_pdf_headers(self):
        """set_pdf_headers устанавливает пользовательские колонтитулы."""
        self.editor.file_export.set_pdf_headers(
            {
                "show_headers": False,
                "header_text": "",
                "footer_text": "",
            }
        )
        headers = self.editor.file_export._get_pdf_headers()
        assert headers["show_headers"] is False
        assert headers["header_text"] == ""
        assert headers["footer_text"] == ""

    def test_set_pdf_headers_preserves_show_flags(self):
        """set_pdf_headers с show_headers=True."""
        self.editor.file_export.set_pdf_headers(
            {
                "show_headers": True,
                "header_text": "My Doc",
                "footer_text": "Page ",
            }
        )
        headers = self.editor.file_export._get_pdf_headers()
        assert headers["show_headers"] is True
        assert headers["header_text"] == "My Doc"
        assert "Page" in headers["footer_text"]
