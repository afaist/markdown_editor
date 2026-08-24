"""Вставки текста и форматирование: жирный, курсив, списки, ссылки, изображения."""

import re
from PyQt6.QtWidgets import QFileDialog, QInputDialog
from PyQt6.QtGui import QTextCursor


class TextInsertions:
    """Методы вставки форматированного текста в QTextEdit."""

    def __init__(self, editor):
        self.editor = (
            editor  # MarkdownEditorPyQt (через self.editor.editor — QTextEdit)
        )

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
            # Вставляем текст с разметкой
            cursor.insertText(f"**{selection}**")
            # Получаем позицию начала вставленного текста
            end_pos = cursor.position()
            start_pos = end_pos - len(selection) - 2  # -2 для "** в начале
            # Устанавливаем курсор с выделением только слова "текст" (без **)
            cursor.setPosition(start_pos)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(selection),
            )
        else:
            # Если было выделение — просто оборачиваем его в **
            cursor.insertText(f"**{selection}**")

        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_italic(self) -> None:
        """Вставить *выделенный* текст."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()

        if not selection:
            selection = "текст"
            # Вставляем текст с разметкой
            cursor.insertText(f"*{selection}*")
            # Получаем позицию конца вставленного текста
            end_pos = cursor.position()
            # Вычисляем позицию начала слова "текст" (без учёта * в начале)
            start_pos = end_pos - len(selection) - 1  # -1 для * в начале

            # Устанавливаем курсор в начало выделяемого текста
            cursor.setPosition(start_pos)
            # Выделяем слово "текст", двигаясь вправо на длину слова
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(selection),
            )
        else:
            # Если было выделение — просто оборачиваем его в *
            cursor.insertText(f"*{selection}*")

        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_unordered_list(self) -> None:
        """Вставить маркированный список."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()

        if not selection:
            text_to_insert = "- элемент списка"
            cursor.insertText(text_to_insert)
            # Получаем позицию конца вставленного текста
            end_pos = cursor.position()
            # Вычисляем позицию начала "элемент списка" (без учёта "- " в начале)
            start_pos = end_pos - len("элемент списка")  # -2 для "- " в начале

            # Устанавливаем курсор в начало выделяемого текста
            cursor.setPosition(start_pos)
            # Выделяем "элемент списка", двигаясь вправо на его длину
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len("элемент списка"),
            )
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
            text, ok2 = QInputDialog.getText(
                self.editor, "Вставить ссылку", "Текст ссылки:"
            )
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
        """Вставляет $...$ и помещает курсор между ними, сохраняя выделенный текст."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()

        if not selection:
            # Если нет выделения, просто вставляем пустые $ $ и помещаем курсор между ними
            cursor.insertText("$$")
            cursor.movePosition(QTextCursor.MoveOperation.Left)
        else:
            # Если есть выделение, оборачиваем его в $ $
            selected_text = selection
            # Удаляем выделенный текст (он будет вставлен внутри $ $)
            cursor.removeSelectedText()
            # Вставляем открывающий $
            cursor.insertText("$")
            # Вставляем ранее выделенный текст
            cursor.insertText(selected_text)
            # Вставляем закрывающий $
            cursor.insertText("$")

        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_block_latex(self) -> None:
        """Вставляет $$\n...\n$$ и помещает курсор между ними (на новую строку), сохраняя выделенный текст."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()

        if not selection:
            # Если нет выделения, вставляем шаблон $$\n\n$$ и помещаем курсор в середину
            cursor.insertText("\n$$\n\n$$")
            # Перемещаем курсор на новую строку между $$
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=3)
        else:
            # Если есть выделение, оборачиваем его в $$\n \n$$
            selected_text = selection
            # Удаляем выделенный текст (он будет вставлен внутри блока)
            cursor.removeSelectedText()
            # Вставляем открывающий $$ и новую строку
            cursor.insertText("\n$$\n")
            # Вставляем ранее выделенный текст
            cursor.insertText(selected_text)
            # Вставляем новую строку и закрывающий $$
            cursor.insertText("\n$$")
            # Перемещаем курсор в конец вставленного текста (после последнего $$)
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=2)

        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    # ─── Заголовки ────────────────────────────────────────────────────────

    def insert_heading(self, level: int) -> None:
        """Вставить заголовок указанного уровня (1–7)."""
        if not 1 <= level <= 7:
            return
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()
        hashes = "#" * level
        if selection:
            # Оборачиваем выделение в заголовок
            cursor.insertText(f"{hashes} {selection}")
        else:
            # Вставляем заголовок и ставим курсор после решёток
            cursor.insertText(f"{hashes} ")
            # cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    # ─── Стили ────────────────────────────────────────────────────────────

    def insert_strikethrough(self) -> None:
        """Вставить ~~зачёркнутый~~ текст."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()

        if not selection:
            selection = "текст"
            # Вставляем текст с разметкой зачёркивания
            cursor.insertText(f"~~{selection}~~")
            # Получаем позицию конца вставленного текста
            end_pos = cursor.position()
            # Вычисляем позицию начала слова "текст" (без учёта ~~ в начале)
            start_pos = end_pos - len(selection) - 2  # -2 для ~~ в начале

            # Устанавливаем курсор в начало выделяемого текста
            cursor.setPosition(start_pos)
            # Выделяем слово "текст", двигаясь вправо на длину слова
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(selection),
            )
        else:
            # Если было выделение — просто оборачиваем его в ~~
            cursor.insertText(f"~~{selection}~~")

        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_inline_code(self) -> None:
        """Вставить `встроенный код`."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()

        if not selection:
            selection = "код"
            # Вставляем текст с разметкой встроенного кода
            cursor.insertText(f"`{selection}`")
            # Получаем позицию конца вставленного текста
            end_pos = cursor.position()
            # Вычисляем позицию начала слова "код" (без учёта ` в начале)
            start_pos = end_pos - len(selection) - 1  # -1 для ` в начале

            # Устанавливаем курсор в начало выделяемого текста
            cursor.setPosition(start_pos)
            # Выделяем слово "код", двигаясь вправо на длину слова
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(selection),
            )
        else:
            # Если было выделение — просто оборачиваем его в `
            cursor.insertText(f"`{selection}`")

        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    # ─── Списки ───────────────────────────────────────────────────────────

    def insert_ordered_list(self) -> None:
        """Вставить нумерованный список."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()

        if not selection:
            text_to_insert = "1. элемент списка"
            cursor.insertText(text_to_insert)
            # Получаем позицию конца вставленного текста
            end_pos = cursor.position()
            # Вычисляем позицию начала "элемент списка" (без учёта "1. " в начале)
            start_pos = end_pos - len("элемент списка")  # -3 для "1. " в начале

            # Устанавливаем курсор в начало выделяемого текста
            cursor.setPosition(start_pos)
            # Выделяем "элемент списка", двигаясь вправо на его длину
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len("элемент списка"),
            )
        else:
            lines = [line for line in selection.split("\n") if line.strip()]
            list_items = "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))
            cursor.insertText(list_items)

        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_task_list(self) -> None:
        """Вставить элемент списка задач (- [ ])."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()

        if not selection:
            text_to_insert = "- [ ] задание"
            cursor.insertText(text_to_insert)
            # Получаем позицию конца вставленного текста
            end_pos = cursor.position()
            # Вычисляем позицию начала "задание" (без учёта "- [ ] " в начале)
            start_pos = end_pos - len("задание")  # -6 для "- [ ] " в начале

            # Устанавливаем курсор в начало выделяемого текста
            cursor.setPosition(start_pos)
            # Выделяем "задание", двигаясь вправо на его длину
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len("задание"),
            )
        else:
            lines = [line for line in selection.split("\n") if line.strip()]
            list_items = "\n".join(f"- [ ] {line}" for line in lines)
            cursor.insertText(list_items)

        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    # ─── Цитата ───────────────────────────────────────────────────────────

    def insert_blockquote(self) -> None:
        """Вставить цитату > ."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()
        if selection:
            lines = selection.split("\n")
            quoted = "\n".join(f"> {line}" for line in lines)
            cursor.insertText(quoted)
        else:
            cursor.insertText("> ")
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    # ─── Код (block) ──────────────────────────────────────────────────────

    def insert_code_block(self, language: str = "") -> None:
        """Вставить блок кода с указанием языка.

        Args:
            language: имя языка подсветки (python, bash, markdown, cpp, rust) или "" для generic.
        """
        cursor = self.editor.editor.textCursor()
        lang = language if language else ""
        if lang:
            template = f"```{lang}\n\n```"
        else:
            template = "```\n\n```"
        cursor.insertText(template)
        # Курсор после ```\n\n``` — двигаемся на 4 символа назад (внутрь блока)
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=4)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    # ─── LaTeX прототипы ─────────────────────────────────────────────────

    def insert_latex_fraction(self) -> None:
        """Вставить \\frac{a}{b} с курсором в первом аргументе."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("\\frac{}{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=3)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_latex_sqrt(self) -> None:
        """Вставить \\sqrt{x} с курсором внутри."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("\\sqrt{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_latex_superscript(self) -> None:
        """Вставить x^{n} с курсором в {}."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("^{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_latex_subscript(self) -> None:
        """Вставить x_{n} с курсором в {}."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("_{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_latex_sum(self) -> None:
        """Вставить \\sum_{i=0}^{n} с курсором в _{}."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("\\sum_{}^{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=4)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_latex_integral(self) -> None:
        """Вставить \\int_{a}^{b} с курсором в _{}."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("\\int_{}^{}")
        cursor.movePosition(QTextCursor.MoveOperation.Left, n=4)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_latex_matrix(self) -> None:
        """Вставить \\begin{matrix}...\\end{matrix} с курсором внутри."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("\\begin{matrix}\n\t& \n\t& \n\\end{matrix}")
        # Переместить курсор на первую пустую ячейку (после \begin{matrix}\n\t)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, n=2)
        cursor.movePosition(QTextCursor.MoveOperation.Right, n=2)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    # ─── Дополнительные вставки ──────────────────────────────────────────

    def insert_horizontal_rule(self) -> None:
        """Вставить горизонтальный разделитель ---."""
        cursor = self.editor.editor.textCursor()
        cursor.insertText("\n---\n")
        cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_table(self) -> None:
        """Вставить таблицу Markdown 3×3 с заголовками."""
        cursor = self.editor.editor.textCursor()
        table = (
            "| Колонка 1 | Колонка 2 | Колонка 3 |\n"
            "|-----------|-----------|----------|\n"
            "| Данные    | Данные    | Данные   |\n"
            "| Данные    | Данные    | Данные   |"
        )
        cursor.insertText(table)
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()

    def insert_html_comment(self) -> None:
        """Вставить HTML-комментарий <!-- -->."""
        cursor = self.editor.editor.textCursor()
        selection = cursor.selectedText()
        if not selection:
            selection = "комментарий"
        cursor.insertText(f"<!-- {selection} -->")
        self.editor.editor.setTextCursor(cursor)
        self.editor.update_preview()
