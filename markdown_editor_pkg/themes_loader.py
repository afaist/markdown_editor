"""Load theme CSS/QSS from files in themes_data/."""

from __future__ import annotations

import importlib.resources


def _read_theme_file(package: str, filename: str) -> str:
    """Read a theme file from the themes_data package."""
    try:
        # Python 3.9+
        with importlib.resources.files(package).joinpath(filename).open(encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback: return empty string
        return ""


def load_preview_themes() -> dict[str, str]:
    """Load all preview CSS themes from files."""
    themes: dict[str, str] = {}
    package = "markdown_editor_pkg.themes_data"

    mapping = [
        ("light", "preview_light.css"),
        ("dark", "preview_dark.css"),
        ("contrast", "preview_contrast.css"),
        ("monokai", "preview_monokai.css"),
        ("dracula", "preview_dracula.css"),
        ("one-dark", "preview_one_dark.css"),
        ("github-dark", "preview_github_dark.css"),
        ("solarized-dark", "preview_solarized_dark.css"),
    ]

    for theme_name, filename in mapping:
        css = _read_theme_file(package, filename)
        if css:
            themes[theme_name] = css

    return themes


def load_editor_themes() -> dict[str, str]:
    """Load all editor QSS themes from files."""
    themes: dict[str, str] = {}
    package = "markdown_editor_pkg.themes_data"

    mapping = [
        ("light", "editor_light.qss"),
        ("dark", "editor_dark.qss"),
        ("contrast", "editor_contrast.qss"),
        ("monokai", "editor_monokai.qss"),
        ("dracula", "editor_dracula.qss"),
        ("one-dark", "editor_one_dark.qss"),
        ("github-dark", "editor_github_dark.qss"),
        ("solarized-dark", "editor_solarized_dark.qss"),
    ]

    for theme_name, filename in mapping:
        qss = _read_theme_file(package, filename)
        if qss:
            themes[theme_name] = qss

    return themes
