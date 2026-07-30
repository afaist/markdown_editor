"""Диалог «Найти и заменить» для QTextEdit."""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)


class FindReplaceDialog:
    """Модальный диалог поиска и замены текста."""

    def __init__(self, editor):
        self.editor = editor  # MarkdownEditorPyQt

    def exec_dialog(self) -> None:
        """Показать диалог и выполнить поиск/замену."""
        dialog = QDialog(self.editor)
        dialog.setWindowTitle("Найти и заменить")
        layout = QVBoxLayout()

        find_label = QLabel("Найти:")
        find_input = QLineEdit()
        replace_label = QLabel("Заменить на:")
        replace_input = QLineEdit()

        layout.addWidget(find_label)
        layout.addWidget(find_input)
        layout.addWidget(replace_label)
        layout.addWidget(replace_input)

        button_layout = QHBoxLayout()
        find_button = QPushButton("Найти следующее")
        replace_button = QPushButton("Заменить")
        cancel_button = QPushButton("Отмена")

        def find_next() -> None:
            text = find_input.text()
            if not text:
                return
            cursor = self.editor.editor.textCursor()
            found = self.editor.editor.find(text)
            if not found:
                cursor.setPosition(0)
                self.editor.editor.setTextCursor(cursor)
                self.editor.editor.find(text)

        def do_replace() -> None:
            text = find_input.text()
            replacement = replace_input.text()
            if not text:
                return
            cursor = self.editor.editor.textCursor()
            if cursor.selectedText() == text:
                cursor.insertText(replacement)
            self.editor.editor.find(text)

        find_button.clicked.connect(find_next)
        replace_button.clicked.connect(do_replace)
        cancel_button.clicked.connect(dialog.close)

        button_layout.addWidget(find_button)
        button_layout.addWidget(replace_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()
