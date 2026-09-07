# markdown_editor_pkg — пакет Markdown Editor (PyQt6)
"""Пакет для Markdown редактора с поддержкой LaTeX."""

from importlib.metadata import version as _version

__all__: list[str] = []

try:
    __version__ = _version("markdown-editor")
except Exception:
    __version__ = "0.0.0.dev0"
