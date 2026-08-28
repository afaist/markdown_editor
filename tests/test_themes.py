"""Tests for theme switching via ThemesManager."""

from markdown_editor_pkg.themes import ThemesManager


class TestThemeSwitching:
    """Тесты переключения тем через ThemesManager."""

    def setup_method(self):
        self.tm = ThemesManager()

    def test_initial_theme_is_light(self):
        """По умолчанию тема предпросмотра — light."""
        assert self.tm.theme_name == "light"

    def test_theme_toggle(self):
        """Переключение темы обновляет theme_name."""
        initial = self.tm.theme_name
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name != initial

        self.tm.toggle_preview_theme()
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "light"

    def test_set_theme(self):
        """set_preview_theme устанавливает нужную тему."""
        self.tm.set_preview_theme("dark")
        assert self.tm.theme_name == "dark"
        self.tm.set_preview_theme("contrast")
        assert self.tm.theme_name == "contrast"

    def test_themes_dict_exists(self):
        """Словарь THEMES_CSS содержит все темы."""
        themes = self.tm.THEMES_CSS
        assert "light" in themes
        assert "dark" in themes
        assert "contrast" in themes
        for theme_name, css in themes.items():
            assert isinstance(css, str)
            assert len(css) > 0


class TestEditorTheme:
    """Тесты переключения темы редактора."""

    def setup_method(self):
        self.tm = ThemesManager()

    def test_initial_editor_theme_is_light(self):
        """Тема редактора по умолчанию — light."""
        assert self.tm.editor_theme == "light"

    def test_toggle_editor_theme_cycles_themes(self):
        """Переключение темы редактора работает по циклу."""
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "dark"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "contrast"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "light"

    def test_editor_themes_dict_exists(self):
        """Словарь EDITOR_STYLES содержит все темы."""
        styles = self.tm.EDITOR_STYLES
        assert "light" in styles
        assert "dark" in styles
        assert "contrast" in styles
        for theme_name, css in styles.items():
            assert isinstance(css, str)
            assert len(css) > 0
