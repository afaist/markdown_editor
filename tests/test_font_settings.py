"""Tests for font settings via ThemesManager."""

from markdown_editor_pkg.editor import MarkdownEditorPyQt
from markdown_editor_pkg.themes import ThemesManager


class TestFontSettings:
    """Тесты управления шрифтом и размером шрифта."""

    def setup_method(self):
        self.tm = ThemesManager()

    def test_initial_font_values(self):
        """По умолчанию шрифт Consolas, размер 11."""
        assert self.tm.font_family == "Consolas"
        assert self.tm.font_size == 11

    def test_default_fonts_list_not_empty(self):
        """Список DEFAULT_FONTS не пустой."""
        assert len(ThemesManager.DEFAULT_FONTS) > 0
        assert "Consolas" in ThemesManager.DEFAULT_FONTS

    def test_get_available_fonts(self):
        """get_available_fonts возвращает список шрифтов."""
        fonts = self.tm.get_available_fonts()
        assert isinstance(fonts, list)
        assert len(fonts) > 0

    def test_increase_font(self):
        """increase_font увеличивает размер шрифта."""
        self.tm._font_size = 10
        old = self.tm._font_size
        self.tm._font_size = min(self.tm.MAX_FONT_SIZE, self.tm._font_size + 1)
        assert self.tm._font_size == old + 1

    def test_decrease_font(self):
        """decrease_font уменьшает размер шрифта."""
        self.tm._font_size = 12
        old = self.tm._font_size
        self.tm._font_size = max(self.tm.MIN_FONT_SIZE, self.tm._font_size - 1)
        assert self.tm._font_size == old - 1

    def test_set_font(self):
        """set_font устанавливает шрифт и размер."""
        self.tm.set_font("Arial", 14, None, persist=False)
        assert self.tm._font_family == "Arial"
        assert self.tm._font_size == 14

    def test_font_family_setter(self):
        """font_family.setter устанавливает имя шрифта."""
        self.tm._font_family = "Arial"
        assert self.tm._font_family == "Arial"

    def test_font_combo_populated_in_editor(self):
        """Комбобокс шрифта в редакторе заполнен."""
        editor = MarkdownEditorPyQt()
        assert editor.font_combo is not None
        assert editor.font_combo.count() > 0
        assert editor.font_combo.currentText() == "Consolas"
        editor.close()

    def test_font_increase_decrease_buttons_exist(self):
        """Кнопки увеличения и уменьшения шрифта существуют."""
        editor = MarkdownEditorPyQt()
        assert editor.font_increase_btn is not None
        assert editor.font_decrease_btn is not None
        assert editor.font_size_label is not None
        editor.close()

    def test_font_increase_decrease_in_editor(self):
        """Кнопки увеличения и уменьшения шрифта работают."""
        editor = MarkdownEditorPyQt()
        initial_size = editor.theme_manager.font_size
        editor._increase_font()
        assert editor.theme_manager.font_size == initial_size + 1
        editor._decrease_font()
        assert editor.theme_manager.font_size == initial_size
        editor.close()

    def test_reset_font_in_editor(self):
        """Сброс шрифта в редакторе работает."""
        editor = MarkdownEditorPyQt()
        editor.theme_manager._font_family = "Arial"
        editor.theme_manager._font_size = 20
        editor.font_combo.setCurrentText("Arial")
        editor._reset_font()
        assert editor.theme_manager.font_family == "Consolas"
        assert editor.theme_manager.font_size == 11
        assert editor.font_combo.currentText() == "Consolas"
        editor.close()
