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
        for _theme_name, css in themes.items():
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
        for _theme_name, css in styles.items():
            assert isinstance(css, str)
            assert len(css) > 0


class TestPreviewCSS:
    """Тесты CSS для предпросмотра."""

    def setup_method(self):
        self.tm = ThemesManager()

    def test_get_preview_css_light(self):
        """CSS light темы содержит body, background-color."""
        css = self.tm.get_preview_css()
        assert "body" in css
        assert "background-color" in css

    def test_get_preview_css_dark(self):
        """CSS dark темы содержит body, background-color: #1e1e1e."""
        self.tm.set_preview_theme("dark")
        css = self.tm.get_preview_css()
        assert "#1e1e1e" in css
        assert "body" in css

    def test_get_preview_css_contrast(self):
        """CSS contrast темы содержит body, background-color: #000000."""
        self.tm.set_preview_theme("contrast")
        css = self.tm.get_preview_css()
        assert "#000000" in css
        assert "body" in css


class TestEditorStyle:
    """Тесты QSS-стилей редактора."""

    def setup_method(self):
        self.tm = ThemesManager()

    def test_get_editor_style_light(self):
        """Светлая тема редактора содержит QTextEdit, background-color: #ffffff."""
        self.tm.editor_theme = "light"
        style = self.tm.get_editor_style()
        assert "QTextEdit" in style
        assert "#ffffff" in style

    def test_get_editor_style_dark(self):
        """Тёмная тема редактора содержит QTextEdit, background-color: #1e1e1e."""
        self.tm.editor_theme = "dark"
        style = self.tm.get_editor_style()
        assert "QTextEdit" in style
        assert "#1e1e1e" in style


class TestThemeCycles:
    """Тесты циклического переключения тем."""

    def setup_method(self):
        self.tm = ThemesManager()

    def test_toggle_preview_theme_cycles(self):
        """Переключение темы предпросмотра: light→dark→contrast→light."""
        assert self.tm.theme_name == "light"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "dark"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "contrast"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "light"

    def test_toggle_editor_theme_cycles(self):
        """Переключение темы редактора: light→dark→contrast→light."""
        assert self.tm.editor_theme == "light"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "dark"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "contrast"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "light"


class TestFontBounds:
    """Тесты границ размера шрифта."""

    def setup_method(self):
        self.tm = ThemesManager()

    def test_font_size_bounds(self):
        """MIN_FONT_SIZE и MAX_FONT_SIZE корректны."""
        assert self.tm.MIN_FONT_SIZE == 6
        assert self.tm.MAX_FONT_SIZE == 72
        assert self.tm.DEFAULT_FONT_SIZE == 11

    def test_set_font_with_none_edit(self):
        """set_font работает с None text_edit."""
        self.tm.set_font("Arial", 14, None)
        assert self.tm._font_family == "Arial"
        assert self.tm._font_size == 14

    def test_reset_font_to_default(self):
        """Сброс шрифта к значениям по умолчанию."""
        self.tm._font_family = "Arial"
        self.tm._font_size = 20
        self.tm.reset_font_to_default(None)
        assert self.tm._font_family == "Consolas"
        assert self.tm._font_size == 11

    def test_increase_font_capped(self):
        """increase_font не превышает MAX_FONT_SIZE."""
        self.tm._font_size = ThemesManager.MAX_FONT_SIZE - 1
        new_size = self.tm.increase_font(None)
        assert new_size == ThemesManager.MAX_FONT_SIZE

    def test_decrease_font_capped(self):
        """decrease_font не меньше MIN_FONT_SIZE."""
        self.tm._font_size = ThemesManager.MIN_FONT_SIZE + 1
        new_size = self.tm.decrease_font(None)
        assert new_size == ThemesManager.MIN_FONT_SIZE
