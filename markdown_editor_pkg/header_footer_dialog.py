"""Header/footer settings dialog for PDF export."""

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from markdown_editor_pkg.i18n import tr


class HeaderFooterDialog(QDialog):
    """Dialog for PDF export header/footer settings."""

    def __init__(self, parent=None, current_headers: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle(tr("PDF Export Settings"))
        self.setModal(True)
        self.setMinimumWidth(400)

        # Значения по умолчанию
        self.show_headers = current_headers.get("show_headers", True) if current_headers else True
        self.header_text = current_headers.get("header_text", "") if current_headers else ""
        self.footer_text = current_headers.get("footer_text", "") if current_headers else ""

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Чекбокс включения колонтитулов
        self.show_cb = QCheckBox(tr("Enable headers"))
        self.show_cb.setChecked(self.show_headers)
        layout.addWidget(self.show_cb)

        # Форма настроек
        form = QFormLayout()

        self.header_edit = QLineEdit()
        self.header_edit.setText(self.header_text)
        self.header_edit.setPlaceholderText(
            tr("Header text (e.g., file name)")
        )
        form.addRow(tr("Header:"), self.header_edit)

        self.footer_edit = QLineEdit()
        self.footer_edit.setText(self.footer_text)
        self.footer_edit.setPlaceholderText(
            tr("Footer text (e.g., markdown_editor)")
        )
        form.addRow(tr("Footer:"), self.footer_edit)

        layout.addLayout(form)

        # Подсказка
        hint = QLabel(
            f"💡 {tr('Tips')}:<br>"
            f"• {tr('Use the file name for the header')}<br>"
            f"• {tr('Footer is visible on every PDF page')}<br>"
            f"• {tr('Page numbering is added automatically (page/total)')}"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(hint)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Управление видимостью
        self.header_edit.setEnabled(self.show_headers)
        self.footer_edit.setEnabled(self.show_headers)
        self.show_cb.toggled.connect(self._toggle_controls)

    def _toggle_controls(self, checked: bool) -> None:
        self.header_edit.setEnabled(checked)
        self.footer_edit.setEnabled(checked)

    def get_headers(self) -> dict:
        """Возвращает настройки колонтитулов."""
        return {
            "show_headers": self.show_cb.isChecked(),
            "header_text": self.header_edit.text().strip(),
            "footer_text": self.footer_edit.text().strip(),
        }
