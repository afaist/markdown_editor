"""Диалог «Найти и заменить» для QTextEdit."""

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class FindReplaceDialog:
    """Модальный диалог поиска и замены текста."""

    def __init__(self, editor):
        self.editor = editor  # MarkdownEditorPyQt

    def exec_dialog(self) -> int:
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

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        find_button = QPushButton("Найти следующее")
        replace_button = QPushButton("Заменить")

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

        # Кнопка Cancel в button_box автоматически вызывает dialog.close() при нажатии
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.close)

        # Добавляем кнопки поиска/замены и кнопки OK/Cancel
        button_layout = QHBoxLayout()
        button_layout.addWidget(find_button)
        button_layout.addWidget(replace_button)
        button_layout.addStretch()  # Чтобы кнопки не растягивались слишком сильно
        button_layout.addWidget(button_box)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        return dialog.exec()
