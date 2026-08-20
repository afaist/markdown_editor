"""Вставки текста и форматирование: жирный, курсив, списки, ссылки, изображения."""

import re
from PyQt6.QtWidgets import QFileDialog, QInputDialog
from PyQt6.QtGui import QTextCursor


class TextInsertions:
    """Методы вставки форматированного текста в QTextEdit."""

    def __init__(self, editor):
        self.editor = editor  # MarkdownEditorPyQt (через self.editor.editor — QTextEdit)

    def insert_text(self, text: str) -> None:
        """Вставка текста в текущую позицию курсора."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()
        if "$" in text and text.count("$") == 1:
            cursor.insertText(text)
        else:
            cursor.insertText(text + selection)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_bold(self) -> None:
        """Вставить **выделенный** текст."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()
        if not selection:
            selection = "текст"
        cursor.insertText(f"**{selection}**")
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_italic(self) -> None:
        """Вставить *выделенный* текст."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()
        if not selection:
            selection = "текст"
        cursor.insertText(f"*{selection}*")
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_unordered_list(self) -> None:
        """Вставить маркированный список."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()
        if not selection:
            cursor.insertText("- элемент списка")
        else:
            lines = selection.split("\n")
            list_items = "\n".join(f"- {line}" for line in lines if line.strip())
            cursor.insertText(list_items)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_link(self) -> None:
        """Вставить ссылку через диалог ввода URL и текста."""
        url, ok1 = QInputDialog.getText(self.editor, "Вставить ссылку", "URL:")
        if ok1 and url:
            text, ok2 = QInputDialog.getText(self.editor, "Вставить ссылку", "Текст ссылки:")
            if ok2:
                cursor = self.editor.editor.textCursor()
                cursor.insertText(f"[{text or url}]({url})")
                self.editor.editor.setTextCursor(cursor)
                self.editor.update_preview()

    def insert_image(self) -> None:
        """Вставить изображение через диалог выбора файла."""
        filepath, _ = QFileDialog.getOpenFileName(
            self.editor,
            "Вставить изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All files (*)",
        )
        if filepath:
            display_path = filepath.replace("\\", "/")
            cursor = self.editor.editor.textCursor()
            image_markdown = f"![изображение]({display_path})"
            cursor.insertText(image_markdown)
            self.editor.editor.setTextCursor(cursor)
            self.editor.update_preview()

    def insert_inline_latex(self) -> None:
        """Вставляет $...$ и помещает курсор между ними."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("$")
        
        # Вставляем закрывающий $
        cursor.insertText("$")
        # Перемещаем курсор на одну позицию назад (внутрь закрывающего $, т.е. между ними)
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_block_latex(self) -> None:
        """Вставляет $$\n$$ и помещает курсор между ними (на новую строку)."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("\n$$\n\n$$")
        # Курсор сейчас в конце второй строки.
        # Нам нужно поставить его в начало второй строки (после первого \n и второго $)
        # Путь: Вверх (к первому \n), Направо (к первому $), Направо (к первому $), Направо (к концу первой строки/началу второй)
        
        # Проще: двигаться назад до начала первой строки, затем вперед на 4 символа ($, $, \n)
        # Но стандартные операции QTextCursor работают посимвольно.
        
        # Алгоритм:
        # 1. Вставили "$$\n$$"
        # 2. Cursor находится сразу после последнего $.
        # 3. Нам нужно переместить его на позицию сразу после "\n$$".
        # Длина вставленного текста без последнего $: 5 символов ($$ + \n + $$) -> нет, 4 символа до последнего символа.
        # Индекс 0: $, 1: $, 2: \n, 3: $, 4: $ (курсор тут, длина 5)
        # Нам нужно индекс 3 (сразу после третьего символа).
        
        # Двигаемся назад на 2 символа (от конца до начала второго $$)
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=3)
        
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()