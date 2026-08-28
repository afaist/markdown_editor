"""Tests for PDF headers in FileOperations."""

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
        headers = self.editor.file_ops._get_pdf_headers()
        assert headers["show_headers"] is True
        assert headers["header_text"] == "Markdown Editor"
        assert "markdown_editor" in headers["footer_text"]
        assert "—" in headers["footer_text"]

    def test_get_pdf_headers_with_file(self):
        """Колонтитулы с открытым файлом используют имя файла."""
        self.editor.current_file = "/home/user/my_document.md"
        headers = self.editor.file_ops._get_pdf_headers()
        assert headers["show_headers"] is True
        assert headers["header_text"] == "my_document.md"
        assert "—" in headers["footer_text"]
