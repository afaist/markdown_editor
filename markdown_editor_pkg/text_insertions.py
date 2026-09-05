"""Вставки текста и форматирование: жирный, курсив, списки, ссылки, изображения."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QFileDialog, QInputDialog

from markdown_editor_pkg.i18n import tr

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QTextEdit


class EditorCursor:
    """Прокси для QTextCursor, убирающий прямой доступ к QTextEdit."""

    def __init__(self, text_edit: QTextEdit) -> None:
        self._edit = text_edit

    @property
    def edit(self) -> QTextEdit:
        return self._edit

    def text_cursor(self) -> QTextCursor:
        """Получить текущий QTextCursor."""
        return self._edit.textCursor()

    def set_text_cursor(self, cursor: QTextCursor) -> None:
        """Установить QTextCursor."""
        self._edit.setTextCursor(cursor)

    def selected_text(self) -> str:
        return self._edit.textCursor().selectedText()

    def full_text(self) -> str:
        return self._edit.toPlainText()

    def insert_text(self, text: str) -> None:
        cursor = self._edit.textCursor()
        cursor.insertText(text)
        self._edit.setTextCursor(cursor)

    def wrap_selection(self, prefix: str, suffix: str, placeholder: str = "") -> None:
        """Оборачивает выделение в prefix/suffix.

        Если выделения нет — вставляет placeholder, обернутый в prefix/suffix,
        и выделяет сам placeholder (без prefix/suffix).
        Если выделен весь документ — считается «пустым выделением».
        """
        cursor = self._edit.textCursor()
        selection = cursor.selectedText()
        full = self.full_text()

        if selection == full and selection:
            selection = ""

        if not selection:
            if not placeholder:
                placeholder = tr("text")
            cursor.insertText(f"{prefix}{placeholder}{suffix}")
            end_pos = cursor.position()
            start_pos = end_pos - len(placeholder) - len(prefix)
            cursor.setPosition(start_pos)
            cursor.setPosition(start_pos + len(placeholder), QTextCursor.MoveMode.KeepAnchor)
        else:
            cursor.insertText(f"{prefix}{selection}{suffix}")

        self._edit.setTextCursor(cursor)


class TextInsertions:
    """Методы вставки форматированного текста в QTextEdit."""

    def __init__(self, editor):
        self.editor = editor

    def _cursor(self) -> EditorCursor:
        return EditorCursor(self.editor.editor)

    def _notify(self) -> None:
        self.editor.update_preview()

    # ─── Вставка текста ─────────────────────────────────────────────────

    def insert_text(self, text: str) -> None:
        """Вставка текста в текущую позицию курсора."""
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()
        if "$" in text and text.count("$") == 1:
            cursor.insertText(text)
        else:
            cursor.insertText(text + selection)
        c.set_text_cursor(cursor)
        self._notify()

    # ─── Стили (wrap) ───────────────────────────────────────────────────

    def insert_bold(self) -> None:
        self._cursor().wrap_selection("**", "**", "текст")
        self._notify()

    def insert_italic(self) -> None:
        self._cursor().wrap_selection("*", "*", "текст")
        self._notify()

    def insert_strikethrough(self) -> None:
        self._cursor().wrap_selection("~~", "~~", "текст")
        self._notify()

    def insert_inline_code(self) -> None:
        self._cursor().wrap_selection("`", "`", "код")
        self._notify()

    # ─── Заголовки ──────────────────────────────────────────────────────

    def insert_heading(self, level: int) -> None:
        if not 1 <= level <= 7:
            return
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()
        full_text = c.full_text()
        # Если файл не пустой — добавляем пустую строку перед заголовком
        if full_text.strip() and not full_text.endswith("\n\n"):
            cursor.insertText("\n")
        hashes = "#" * level
        if selection:
            cursor.insertText(f"{hashes} {selection}")
        else:
            cursor.insertText(f"{hashes} ")
        c.set_text_cursor(cursor)
        self._notify()

    def insert_heading_by_level(self, level: int) -> None:
        """Вставка заголовка уровня level (1–6) — вызывается из комбобокса."""
        self.insert_heading(level)

    # ─── Списки ─────────────────────────────────────────────────────────

    def insert_unordered_list(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()
        full = c.full_text()

        if selection == full and selection:
            selection = ""

        if not selection:
            # Если текст не пустой и не заканчивается пустой строкой, добавляем пустую строку
            if full.strip() and not full.endswith("\n\n"):
                cursor.insertText("\n")
            text_to_insert = "- элемент списка"
            cursor.insertText(text_to_insert)
            end_pos = cursor.position()
            start_pos = end_pos - len("элемент списка")
            cursor.setPosition(start_pos)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len("элемент списка"),
            )
        else:
            lines = selection.split("\n")
            list_items = "\n".join(f"- {line}" for line in lines if line.strip())
            cursor.insertText(list_items)

        c.set_text_cursor(cursor)
        self._notify()

    def insert_ordered_list(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()
        full = c.full_text()

        if selection == full and selection:
            selection = ""

        if not selection:
            # Если текст не пустой и не заканчивается пустой строкой, добавляем пустую строку
            if full.strip() and not full.endswith("\n\n"):
                cursor.insertText("\n")
            text_to_insert = "1. элемент списка"
            cursor.insertText(text_to_insert)
            end_pos = cursor.position()
            start_pos = end_pos - len("элемент списка")
            cursor.setPosition(start_pos)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len("элемент списка"),
            )
        else:
            lines = [line for line in selection.split("\n") if line.strip()]
            list_items = "\n".join(f"{i + 1}. {line}" for i, line in enumerate(lines))
            cursor.insertText(list_items)

        c.set_text_cursor(cursor)
        self._notify()

    def insert_task_list(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()
        full = c.full_text()

        if selection == full and selection:
            selection = ""

        if not selection:
            # Если текст не пустой и не заканчивается пустой строкой, добавляем пустую строку
            if full.strip() and not full.endswith("\n\n"):
                cursor.insertText("\n")
            text_to_insert = tr("- [ ] task")
            cursor.insertText(text_to_insert)
            end_pos = cursor.position()
            start_pos = end_pos - len(tr("task"))
            cursor.setPosition(start_pos)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(tr("task")),
            )
        else:
            lines = [line for line in selection.split("\n") if line.strip()]
            list_items = "\n".join(f"- [ ] {line}" for line in lines)
            cursor.insertText(list_items)

        c.set_text_cursor(cursor)
        self._notify()

    # ─── Цитата ─────────────────────────────────────────────────────────

    def insert_blockquote(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()
        if selection:
            lines = selection.split("\n")
            quoted = "\n".join(f"> {line}" for line in lines)
            cursor.insertText(quoted)
        else:
            cursor.insertText("> ")
        c.set_text_cursor(cursor)
        self._notify()

    # ─── Код (block) ────────────────────────────────────────────────────

    def insert_code_block(self, language: str = "") -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        lang = language if language else ""
        if lang:
            template = f"```{lang}\n\n```"
        else:
            template = "```\n\n```"
        cursor.insertText(template)
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=4)
        c.set_text_cursor(cursor)
        self._notify()

    # ─── LaTeX ──────────────────────────────────────────────────────────

    def insert_inline_latex(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()
        full = c.full_text()

        if selection == full and selection:
            selection = ""

        if not selection:
            cursor.insertText("$$")
            cursor.movePosition(QTextCursor.MoveOperation.Left)
        else:
            cursor.removeSelectedText()
            cursor.insertText("$")
            cursor.insertText(selection)
            cursor.insertText("$")

        c.set_text_cursor(cursor)
        self._notify()

    def insert_block_latex(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()

        if not selection:
            cursor.insertText("\n$$\n\n$$")
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=3)
        else:
            cursor.removeSelectedText()
            cursor.insertText("\n$$\n")
            cursor.insertText(selection)
            cursor.insertText("\n$$")
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=2)

        c.set_text_cursor(cursor)
        self._notify()

    def insert_latex_fraction(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        cursor.insertText("\\frac{}{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=3)
        c.set_text_cursor(cursor)
        self._notify()

    def insert_latex_sqrt(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        cursor.insertText("\\sqrt{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        c.set_text_cursor(cursor)
        self._notify()

    def insert_latex_superscript(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        cursor.insertText("^{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        c.set_text_cursor(cursor)
        self._notify()

    def insert_latex_subscript(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        cursor.insertText("_{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        c.set_text_cursor(cursor)
        self._notify()

    def insert_latex_sum(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        cursor.insertText("\\sum_{}^{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=4)
        c.set_text_cursor(cursor)
        self._notify()

    def insert_latex_integral(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        cursor.insertText("\\int_{}^{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=4)
        c.set_text_cursor(cursor)
        self._notify()

    def insert_latex_matrix(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        cursor.insertText("\\begin{matrix}\n\t& \n\t& \n\\end{matrix}")
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, n=2)
        cursor.movePosition(QTextCursor.MoveOperation.Right, n=2)
        c.set_text_cursor(cursor)
        self._notify()

    # ─── Ссылки и изображения ───────────────────────────────────────────

    def insert_link(self) -> None:
        url, ok1 = QInputDialog.getText(self.editor, "Вставить ссылку", "URL:")
        if ok1 and url:
            text, ok2 = QInputDialog.getText(self.editor, "Вставить ссылку", "Текст ссылки:")
            if ok2:
                c = self._cursor()
                cursor = c.text_cursor()
                cursor.insertText(f"[{text or url}]({url})")
                c.set_text_cursor(cursor)
                self._notify()

    def insert_image(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self.editor,
            "Вставить изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All files (*)",
        )
        if filepath:
            display_path = filepath.replace("\\", "/")
            c = self._cursor()
            cursor = c.text_cursor()
            cursor.insertText(f"![изображение]({display_path})")
            c.set_text_cursor(cursor)
            self._notify()

    # ─── Дополнительные вставки ─────────────────────���───────────────────

    def insert_horizontal_rule(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        cursor.insertText("\n---\n")
        cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter)
        c.set_text_cursor(cursor)
        self._notify()

    def insert_table(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        table = (
            "| Колонка 1 | Колонка 2 | Колонка 3 |\n"
            "|-----------|-----------|----------|\n"
            "| Данные    | Данные    | Данные   |\n"
            "| Данные    | Данные    | Данные   |"
        )
        cursor.insertText(table)
        c.set_text_cursor(cursor)
        self._notify()

    def insert_html_comment(self) -> None:
        c = self._cursor()
        cursor = c.text_cursor()
        selection = cursor.selectedText()
        if not selection:
            selection = "комментарий"
        cursor.insertText(f"<!-- {selection} -->")
        c.set_text_cursor(cursor)
