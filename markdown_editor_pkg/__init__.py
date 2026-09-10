# markdown_editor_pkg — пакет Markdown Editor (PyQt6)
"""Пакет для Markdown редактора с поддержкой LaTeX."""

from importlib.metadata import version as _version

__all__: list[str] = []


def _get_version() -> str:
    """Return package version from installed metadata or setuptools_scm."""
    # 1. Installed package metadata
    try:
        return _version("markdown-editor")
    except Exception:
        pass

    # 2. setuptools_scm (editable install or direct import)
    try:
        from setuptools_scm import get_version

        return get_version()
    except Exception:
        pass

    return "0.0.0.dev0"


__version__ = _get_version()
