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
        assert self.tm.theme_name == "monokai"

    def test_set_theme(self):
        """set_preview_theme устанавливает нужную тему."""
        self.tm.set_preview_theme("dark")
        assert self.tm.theme_name == "dark"
        self.tm.set_preview_theme("contrast")
        assert self.tm.theme_name == "contrast"

    def test_themes_dict_exists(self):
        """Словарь THEMES_CSS содержит все темы."""
        themes = self.tm.THEMES_CSS
        for theme in (
            "light",
            "dark",
            "contrast",
            "monokai",
            "dracula",
            "one-dark",
            "github-dark",
            "solarized-dark",
        ):
            assert theme in themes
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
        assert self.tm.editor_theme == "monokai"

    def test_editor_themes_dict_exists(self):
        """Словарь EDITOR_STYLES содержит все темы."""
        styles = self.tm.EDITOR_STYLES
        for theme in (
            "light",
            "dark",
            "contrast",
            "monokai",
            "dracula",
            "one-dark",
            "github-dark",
            "solarized-dark",
        ):
            assert theme in styles
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

    def test_get_preview_css_monokai(self):
        """CSS monokai темы содержит body, background-color: #272822."""
        self.tm.set_preview_theme("monokai")
        css = self.tm.get_preview_css()
        assert "#272822" in css
        assert "body" in css

    def test_get_preview_css_dracula(self):
        """CSS dracula темы содержит body, background-color: #282A36."""
        self.tm.set_preview_theme("dracula")
        css = self.tm.get_preview_css()
        assert "#282A36" in css
        assert "body" in css

    def test_get_preview_css_one_dark(self):
        """CSS one-dark темы содержит body, background-color: #282C34."""
        self.tm.set_preview_theme("one-dark")
        css = self.tm.get_preview_css()
        assert "#282C34" in css
        assert "body" in css

    def test_get_preview_css_github_dark(self):
        """CSS github-dark темы содержит body, background-color: #0D1117."""
        self.tm.set_preview_theme("github-dark")
        css = self.tm.get_preview_css()
        assert "#0D1117" in css
        assert "body" in css

    def test_get_preview_css_solarized_dark(self):
        """CSS solarized-dark темы содержит body, background-color: #002B36."""
        self.tm.set_preview_theme("solarized-dark")
        css = self.tm.get_preview_css()
        assert "#002B36" in css
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

    def test_get_editor_style_monokai(self):
        """Тема Monokai редактора содержит QTextEdit, background-color: #272822."""
        self.tm.editor_theme = "monokai"
        style = self.tm.get_editor_style()
        assert "QTextEdit" in style
        assert "#272822" in style

    def test_get_editor_style_dracula(self):
        """Тема Dracula редактора содержит QTextEdit, background-color: #282A36."""
        self.tm.editor_theme = "dracula"
        style = self.tm.get_editor_style()
        assert "QTextEdit" in style
        assert "#282A36" in style

    def test_get_editor_style_one_dark(self):
        """Тема One Dark редактора содержит QTextEdit, background-color: #282C34."""
        self.tm.editor_theme = "one-dark"
        style = self.tm.get_editor_style()
        assert "QTextEdit" in style
        assert "#282C34" in style

    def test_get_editor_style_github_dark(self):
        """Тема GitHub Dark редактора содержит QTextEdit, background-color: #0D1117."""
        self.tm.editor_theme = "github-dark"
        style = self.tm.get_editor_style()
        assert "QTextEdit" in style
        assert "#0D1117" in style

    def test_get_editor_style_solarized_dark(self):
        """Тема Solarized Dark редактора содержит QTextEdit, background-color: #002B36."""
        self.tm.editor_theme = "solarized-dark"
        style = self.tm.get_editor_style()
        assert "QTextEdit" in style
        assert "#002B36" in style


class TestThemeCycles:
    """Тесты циклического переключения тем."""

    def setup_method(self):
        self.tm = ThemesManager()

    def test_toggle_preview_theme_cycles(self):
        """Переключение темы предпросмотра: light→dark→contrast→monokai→…→light."""
        assert self.tm.theme_name == "light"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "dark"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "contrast"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "monokai"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "dracula"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "one-dark"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "github-dark"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "solarized-dark"
        self.tm.toggle_preview_theme()
        assert self.tm.theme_name == "light"

    def test_toggle_editor_theme_cycles(self):
        """Переключение темы редактора: light→dark→contrast→monokai→…→light."""
        assert self.tm.editor_theme == "light"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "dark"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "contrast"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "monokai"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "dracula"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "one-dark"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "github-dark"
        self.tm.toggle_editor_theme()
        assert self.tm.editor_theme == "solarized-dark"
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


class TestThemePersistence:
    """Тесты сохранения тем в Settings."""

    def test_set_theme_saves_to_settings(self, tmp_path, monkeypatch):
        """set_preview_theme сохраняет тему в Settings."""
        from markdown_editor_pkg import settings as settings_mod

        config_path = tmp_path / "test_config.json"
        monkeypatch.setattr(settings_mod, "CONFIG_FILE", config_path)

        tm = ThemesManager()
        tm.set_preview_theme("dracula")

        # Новый экземпляр Settings читает тот же файл
        from markdown_editor_pkg.settings import Settings

        settings = Settings()
        assert settings.get("theme") == "dracula"

    def test_set_editor_theme_saves_to_settings(self, tmp_path, monkeypatch):
        """set_editor_theme сохраняет тему в Settings."""
        from markdown_editor_pkg import settings as settings_mod

        config_path = tmp_path / "test_config.json"
        monkeypatch.setattr(settings_mod, "CONFIG_FILE", config_path)

        tm = ThemesManager()
        tm.set_editor_theme("monokai")

        from markdown_editor_pkg.settings import Settings

        settings = Settings()
        assert settings.get("editor_theme") == "monokai"

    def test_settings_loads_saved_theme(self, tmp_path):
        """Settings загружает сохранённую тему."""
        from markdown_editor_pkg.settings import Settings

        config_path = tmp_path / "test_config.json"
        # Сначала сохраняем
        settings = Settings(config_path=config_path)
        settings.set("theme", "github-dark")
        settings.set("editor_theme", "solarized-dark")

        # Затем загружаем в новом экземпляре
        settings2 = Settings(config_path=config_path)
        assert settings2.get("theme") == "github-dark"
        assert settings2.get("editor_theme") == "solarized-dark"

    def test_font_settings_saves_to_settings(self, tmp_path, monkeypatch):
        """Настройки шрифта сохраняются в Settings."""
        from markdown_editor_pkg import settings as settings_mod

        config_path = tmp_path / "test_config.json"
        monkeypatch.setattr(settings_mod, "CONFIG_FILE", config_path)

        tm = ThemesManager()
        tm.set_font("JetBrains Mono", 16, None)

        from markdown_editor_pkg.settings import Settings

        settings = Settings()
        assert settings.get("editor_font") == "JetBrains Mono"
        assert settings.get("editor_font_size") == 16

    def test_toggle_theme_saves_to_settings(self, tmp_path, monkeypatch):
        """toggle_preview_theme сохраняет новую тему в Settings."""
        from markdown_editor_pkg import settings as settings_mod

        config_path = tmp_path / "test_config.json"
        monkeypatch.setattr(settings_mod, "CONFIG_FILE", config_path)

        tm = ThemesManager()
        tm.set_preview_theme("light")

        from markdown_editor_pkg.settings import Settings

        settings = Settings()
        assert settings.get("theme") == "light"

        tm.toggle_preview_theme()
        settings = Settings()
        assert settings.get("theme") == "dark"

        tm.toggle_preview_theme()
        settings = Settings()
        assert settings.get("theme") == "contrast"
