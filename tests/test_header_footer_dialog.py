"""Tests for HeaderFooterDialog."""

from markdown_editor_pkg.header_footer_dialog import HeaderFooterDialog


class TestHeaderFooterDialog:
    """Тесты диалога настроек колонтитулов."""

    def test_dialog_creates(self):
        """Диалог создаётся без ошибок."""
        dialog = HeaderFooterDialog()
        assert dialog.windowTitle() == "Настройки PDF-экспорта"
        assert dialog.show_cb is not None
        assert dialog.header_edit is not None
        assert dialog.footer_edit is not None
        dialog.close()

    def test_get_headers_default(self):
        """Значения по умолчанию: show_headers=True."""
        dialog = HeaderFooterDialog()
        headers = dialog.get_headers()
        assert headers["show_headers"] is True
        dialog.close()

    def test_get_headers_custom(self):
        """Кастомные значения header/footer."""
        current = {
            "show_headers": True,
            "header_text": "Мой заголовок",
            "footer_text": "Мой футер",
        }
        dialog = HeaderFooterDialog(current_headers=current)
        headers = dialog.get_headers()
        assert headers["header_text"] == "Мой заголовок"
        assert headers["footer_text"] == "Мой футер"
        dialog.close()

    def test_toggle_controls(self):
        """При отключении чекбокса редакторы блокируются."""
        dialog = HeaderFooterDialog()
        # Изначально включено
        assert dialog.header_edit.isEnabled() is True
        assert dialog.footer_edit.isEnabled() is True

        # Отключаем
        dialog.show_cb.setChecked(False)
        dialog._toggle_controls(False)
        assert dialog.header_edit.isEnabled() is False
        assert dialog.footer_edit.isEnabled() is False

        # Включаем обратно
        dialog.show_cb.setChecked(True)
        dialog._toggle_controls(True)
        assert dialog.header_edit.isEnabled() is True
        assert dialog.footer_edit.isEnabled() is True
        dialog.close()

    def test_get_headers_disabled(self):
        """При отключённых колонтитулах show_headers=False."""
        dialog = HeaderFooterDialog()
        dialog.show_cb.setChecked(False)
        headers = dialog.get_headers()
        assert headers["show_headers"] is False
        dialog.close()
