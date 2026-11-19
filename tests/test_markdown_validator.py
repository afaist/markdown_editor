"""Tests for markdown_validator module."""

from PyQt6.QtWidgets import QApplication

from markdown_editor_pkg.markdown_validator import (
    MarkdownIssue,
    MarkdownValidator,
    ValidationReport,
)

# Shared QApplication for ValidationLabel tests
_qapp = QApplication.instance()
if _qapp is None:
    _qapp = QApplication([])


class TestValidationReport:
    """Тесты ValidationReport."""

    def test_is_valid_when_no_issues(self):
        """Report без проблем — is_valid = True."""
        report = ValidationReport()
        assert report.is_valid is True

    def test_is_valid_when_only_warnings(self):
        """Report только с предупреждениями — is_valid = True."""
        report = ValidationReport(issues=[MarkdownIssue(severity="warning", message="test")])
        assert report.is_valid is True

    def test_is_valid_when_has_errors(self):
        """Report с ошибками — is_valid = False."""
        report = ValidationReport(issues=[MarkdownIssue(severity="error", message="test")])
        assert report.is_valid is False

    def test_error_count(self):
        """Подсчёт ошибок."""
        report = ValidationReport(
            issues=[
                MarkdownIssue(severity="error", message="e1"),
                MarkdownIssue(severity="error", message="e2"),
                MarkdownIssue(severity="warning", message="w1"),
            ]
        )
        assert report.error_count == 2
        assert report.warning_count == 1
        assert report.info_count == 0

    def test_summary_empty(self):
        """Summary без проблем."""
        report = ValidationReport()
        assert report.summary == "No issues found"

    def test_summary_with_issues(self):
        """Summary с проблемами."""
        report = ValidationReport(
            issues=[
                MarkdownIssue(severity="error", message="e1"),
                MarkdownIssue(severity="warning", message="w1"),
                MarkdownIssue(severity="info", message="i1"),
            ]
        )
        assert "Errors: 1" in report.summary
        assert "Warnings: 1" in report.summary
        assert "Info: 1" in report.summary


class TestUnclosedCodeBlocks:
    """Тесты проверки незакрытых блоков кода."""

    def test_valid_code_block(self):
        """Корректный блок кода."""
        text = "```python\nprint('hello')\n```"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_unclosed_code_block(self):
        """Незакрытый блок кода."""
        text = "```python\nprint('hello')"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is False
        assert report.error_count >= 1

    def test_multiple_code_blocks(self):
        """Несколько корректных блоков кода."""
        text = "```python\nprint('a')\n```\n\n```js\nconsole.log('b')\n```"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_nested_backticks_in_code_block(self):
        """Бэктки внутри блока кода."""
        text = "```\n`hello`\n```"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True


class TestUnclosedInlineFormatting:
    """Тесты проверки незакрытого inline-форматирования."""

    def test_valid_bold(self):
        """Корректный bold."""
        text = "This is **bold** text"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_valid_italic(self):
        """Корректный italic."""
        text = "This is *italic* text"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_unclosed_bold(self):
        """Незакрытый bold."""
        text = "This is **bold text"
        report = MarkdownValidator().validate(text)
        assert report.error_count == 0  # warning, not error
        assert report.warning_count >= 1

    def test_valid_strikethrough(self):
        """Корректный strikethrough."""
        text = "This is ~~strikethrough~~ text"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_unclosed_strikethrough(self):
        """Незакрытый strikethrough."""
        text = "This is ~~strikethrough text"
        report = MarkdownValidator().validate(text)
        assert report.warning_count >= 1

    def test_valid_inline_code(self):
        """Корректный inline code."""
        text = "Use `code` here"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_unclosed_inline_code(self):
        """Незакрытый inline code."""
        text = "Use `code here"
        report = MarkdownValidator().validate(text)
        # Нечётное количество бэктков — error
        assert report.error_count >= 1


class TestEmptyLinksAndImages:
    """Тесты проверки пустых ссылок и изображений."""

    def test_valid_link(self):
        """Корректная ссылка."""
        text = "[Google](https://google.com)"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_valid_image(self):
        """Корректное изображение."""
        text = "![Alt text](image.png)"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_empty_link(self):
        """Пустая ссылка."""
        text = "[]()"
        report = MarkdownValidator().validate(text)
        assert report.warning_count >= 1

    def test_empty_image(self):
        """Пустое изображение."""
        text = "![]()"
        report = MarkdownValidator().validate(text)
        assert report.warning_count >= 1

    def test_link_without_url(self):
        """Ссылка без URL."""
        text = "[text]()"
        report = MarkdownValidator().validate(text)
        assert report.warning_count >= 1

    def test_image_without_url(self):
        """Изображение без URL."""
        text = "![alt]()"
        report = MarkdownValidator().validate(text)
        assert report.warning_count >= 1


class TestUnclosedLinkBrackets:
    """Тесты проверки незакрытых квадратных скобок."""

    def test_valid_link_bracket(self):
        """Корректная ссылка."""
        text = "[text](url)"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_unclosed_link_bracket(self):
        """Незакрытая скобка."""
        text = "[text"
        report = MarkdownValidator().validate(text)
        assert report.error_count >= 1

    def test_multiple_brackets(self):
        """Несколько ссылок."""
        text = "[a](b) and [c](d)"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_brackets_in_code(self):
        """Скобки в коде не проверяются."""
        text = "```\n[not a link]\n```"
        report = MarkdownValidator().validate(text)
        # Не должно быть ошибок из-за скобок
        bracket_errors = [i for i in report.issues if "[" in i.message]
        assert len(bracket_errors) == 0


class TestListConsistency:
    """Тесты проверки согласованности списков."""

    def test_valid_unordered_list(self):
        """Корректный маркированный список."""
        text = "- item 1\n- item 2\n- item 3"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_valid_ordered_list(self):
        """Корректный нумерованный список."""
        text = "1. first\n2. second\n3. third"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_mixed_list_markers(self):
        """Смешанные маркеры списка."""
        text = "- item 1\n* item 2\n- item 3"
        report = MarkdownValidator().validate(text)
        # Это info, не error
        assert report.is_valid is True


class TestTrailingWhitespace:
    """Тесты проверки завершающих пробелов."""

    def test_no_trailing_whitespace(self):
        """Нет завершающих пробелов."""
        text = "line 1\nline 2\nline 3"
        report = MarkdownValidator().validate(text)
        info_issues = [i for i in report.issues if i.severity == "info"]
        trailing = [i for i in info_issues if "trailing" in i.message.lower()]
        assert len(trailing) == 0

    def test_with_trailing_whitespace(self):
        """Есть завершающие пробелы."""
        text = "line 1   \nline 2\nline 3  "
        report = MarkdownValidator().validate(text)
        info_issues = [i for i in report.issues if i.severity == "info"]
        trailing = [i for i in info_issues if "trailing" in i.message.lower()]
        assert len(trailing) >= 1


class TestMultipleBlankLines:
    """Тесты проверки множественных пустых строк."""

    def test_no_consecutive_blanks(self):
        """Нет последовательных пустых строк."""
        text = "line 1\nline 2\nline 3"
        report = MarkdownValidator().validate(text)
        blank_issues = [i for i in report.issues if "blank" in i.message.lower()]
        assert len(blank_issues) == 0

    def test_three_consecutive_blanks(self):
        """Три пустые строки подряд."""
        text = "line 1\n\n\n\nline 2"
        report = MarkdownValidator().validate(text)
        blank_issues = [i for i in report.issues if "blank" in i.message.lower()]
        assert len(blank_issues) >= 1


class TestHtmlTags:
    """Тесты проверки HTML-тегов."""

    def test_valid_html(self):
        """Корректный HTML-тег."""
        text = "Some <strong>text</strong>"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_void_element(self):
        """Void-элемент не проверяется."""
        text = "Line break: <br>"
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_unclosed_html_tag(self):
        """Незакрытый HTML-тег."""
        text = "Some <strong>text"
        report = MarkdownValidator().validate(text)
        assert report.warning_count >= 1

    def test_html_in_code_block(self):
        """HTML в коде не проверяется."""
        text = "```\n<div>hello</div>\n```"
        report = MarkdownValidator().validate(text)
        html_issues = [
            i for i in report.issues if "HTML" in i.message or "tag" in i.message.lower()
        ]
        assert len(html_issues) == 0


class TestIsInsideCodeBlock:
    """Тесты проверки нахождения внутри блока кода."""

    def test_first_line_not_in_code(self):
        """Первая строка не внутри кода."""
        lines = ["line 1", "line 2"]
        assert MarkdownValidator._is_inside_code_block(lines, 0) is False

    def test_inside_code_block(self):
        """Строка внутри блока кода."""
        lines = ["```", "line 1", "line 2", "```"]
        assert MarkdownValidator._is_inside_code_block(lines, 1) is True
        assert MarkdownValidator._is_inside_code_block(lines, 2) is True

    def test_after_code_block(self):
        """Строка после блока кода."""
        lines = ["```", "line 1", "```", "line 2"]
        assert MarkdownValidator._is_inside_code_block(lines, 3) is False

    def test_out_of_bounds(self):
        """Выход за границы."""
        lines = ["line 1"]
        assert MarkdownValidator._is_inside_code_block(lines, -1) is False
        assert MarkdownValidator._is_inside_code_block(lines, 5) is False


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_empty_text(self):
        """Пустой текст."""
        report = MarkdownValidator().validate("")
        assert report.is_valid is True
        assert len(report.issues) == 0

    def test_only_whitespace(self):
        """Только пробелы."""
        report = MarkdownValidator().validate("   \n  \n   ")
        assert report.is_valid is True

    def test_complex_document(self):
        """Сложный документ с несколькими элементами."""
        text = """# Title

This is **bold** and *italic* text.

- Item 1
- Item 2

```python
print("hello")
```

[Link](https://example.com)

![Image](image.png)

~~Strikethrough~~

Inline `code` here."""
        report = MarkdownValidator().validate(text)
        assert report.is_valid is True

    def test_multiple_issues(self):
        """Несколько проблем в тексте."""
        text = """Unclosed **bold

[]()

<div>unclosed

```python
incomplete"""
        report = MarkdownValidator().validate(text)
        # Должно быть несколько проблем
        assert len(report.issues) >= 3
        assert report.is_valid is False


class TestDetailsText:
    """Тесты для details_text."""

    def test_empty_report(self):
        """details_text для пустого отчёта."""
        report = ValidationReport()
        assert "No issues found" in report.details_text

    def test_with_issues(self):
        """details_text с проблемами."""
        report = ValidationReport(
            issues=[
                MarkdownIssue(severity="error", message="Bad bracket", line=5),
                MarkdownIssue(severity="warning", message="Trailing space", line=10, char=3),
            ]
        )
        text = report.details_text
        assert "Error" in text
        assert "Warning" in text
        assert "line: 5" in text
        assert "line: 10" in text
        assert "Bad bracket" in text
        assert "Trailing space" in text

    def test_severity_icons(self):
        """Проверка иконок в details_text."""
        report = ValidationReport(
            issues=[
                MarkdownIssue(severity="error", message="err"),
                MarkdownIssue(severity="warning", message="warn"),
                MarkdownIssue(severity="info", message="info"),
            ]
        )
        text = report.details_text
        assert "✕" in text
        assert "⚠" in text
        assert "ℹ" in text


class TestValidationLabel:
    """Тесты для ValidationLabel."""

    def test_label_creation(self):
        """ValidationLabel создаётся."""
        from markdown_editor_pkg.editor_components import ValidationLabel

        label = ValidationLabel()
        assert label.text() == ""
        assert label._validation_report is None

    def test_label_with_text(self):
        """ValidationLabel с текстом."""
        from markdown_editor_pkg.editor_components import ValidationLabel

        label = ValidationLabel("test")
        assert label.text() == "test"

    def test_label_with_report(self):
        """ValidationLabel с отчётом."""
        from markdown_editor_pkg.editor_components import ValidationLabel

        label = ValidationLabel()
        report = ValidationReport(
            issues=[MarkdownIssue(severity="error", message="test error", line=1)]
        )
        label._validation_report = report
        assert label._validation_report is report
        assert label._validation_report.error_count == 1
