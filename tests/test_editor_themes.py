"""Tests for editor_themes module."""

from unittest import mock


class TestThemeFontHandler:
    """Тесты ThemeFontHandler."""

    def test_init(self, markdown_editor):
        """ThemeFontHandler инициализируется с ссылкой на editor."""
        handler = markdown_editor.theme_font_handler
        assert handler.editor is markdown_editor

    def test_toggle_theme_updates_preview(self, markdown_editor):
        """toggle_theme обновляет превью."""
        handler = markdown_editor.theme_font_handler

        with (
            mock.patch.object(markdown_editor.theme_manager, "toggle_preview_theme") as mock_toggle,
            mock.patch.object(markdown_editor, "update_preview") as mock_update,
        ):
            mock_toggle.return_value = "dark"
            handler.toggle_theme()

            mock_toggle.assert_called_once()
            mock_update.assert_called_once()

    def test_set_theme_updates_preview(self, markdown_editor):
        """set_theme устанавливает тему и обновляет превью."""
        handler = markdown_editor.theme_font_handler

        with mock.patch.object(markdown_editor, "update_preview") as mock_update:
            handler.set_theme("dark")

            assert markdown_editor.theme_manager.theme_name == "dark"
            mock_update.assert_called_once()

    def test_toggle_editor_theme(self, markdown_editor):
        """toggle_editor_theme переключает тему редактора."""
        handler = markdown_editor.theme_font_handler

        with mock.patch.object(markdown_editor.theme_manager, "toggle_editor_theme") as mock_toggle:
            mock_toggle.return_value = "dark"
            handler.toggle_editor_theme()

            mock_toggle.assert_called_once()

    def test_set_editor_theme(self, markdown_editor):
        """set_editor_theme устанавливает тему редактора."""
        handler = markdown_editor.theme_font_handler

        handler.set_editor_theme("dark")

        assert markdown_editor.theme_manager.editor_theme == "dark"

    def test_on_font_changed(self, markdown_editor):
        """on_font_changed устанавливает шрифт."""
        handler = markdown_editor.theme_font_handler

        handler.on_font_changed("Consolas")

        # Шрифт должен быть установлен
        assert markdown_editor.theme_manager.font_family == "Consolas"

    def test_increase_font(self, markdown_editor):
        """increase_font увеличивает размер шрифта."""
        handler = markdown_editor.theme_font_handler

        old_size = markdown_editor.theme_manager.font_size
        handler.increase_font()

        assert markdown_editor.theme_manager.font_size > old_size

    def test_decrease_font(self, markdown_editor):
        """decrease_font уменьшает размер шрифта."""
        handler = markdown_editor.theme_font_handler

        old_size = markdown_editor.theme_manager.font_size
        handler.decrease_font()

        assert markdown_editor.theme_manager.font_size < old_size

    def test_reset_font(self, markdown_editor):
        """reset_font сбрасывает шрифт к значениям по умолчанию."""
        handler = markdown_editor.theme_font_handler

        handler.reset_font()

        # Шрифт должен быть сброшен
        assert (
            markdown_editor.theme_manager.font_family in markdown_editor.theme_manager.DEFAULT_FONTS
        )

    def test_update_font_size_label(self, markdown_editor):
        """_update_font_size_label обновляет метку."""
        handler = markdown_editor.theme_font_handler

        handler._update_font_size_label()

        assert markdown_editor.font_size_label is not None
        assert (
            str(markdown_editor.theme_manager.font_size) in markdown_editor.font_size_label.text()
        )

    def test_toggle_theme_with_statusbar(self, markdown_editor):
        """toggle_theme показывает статус в statusbar."""
        handler = markdown_editor.theme_font_handler
        markdown_editor._statusbar_ref = mock.Mock()

        with mock.patch.object(
            markdown_editor.theme_manager, "toggle_preview_theme"
        ) as mock_toggle:
            mock_toggle.return_value = "dark"
            handler.toggle_theme()

            markdown_editor._statusbar_ref.showMessage.assert_called()
