"""resource_path.py — Хелпер для определения путей к ресурсам.

Работает как в режиме разработки, так и в собранном бинарнике PyInstaller.
Используется для корректной загрузки katex/, prism/ и других ресурсов.
"""

from __future__ import annotations

import os
import sys


def resource_path(relative: str) -> str:
    """Возвращает абсолютный путь к ресурсу.

    В режиме разработки: <project_root>/markdown_editor_pkg/<relative>
    В собранном бинарнике: <temp_extract>/<relative> (sys._MEIPASS)

    Args:
        relative: Относительный путь к ресурсу относительно markdown_editor_pkg/

    Returns:
        Абсолютный путь к ресурсу
    """
    # PyInstaller режимы:
    # - onefile: sys._MEIPASS указывает на временную распакованную папку
    # - onedir: sys.frozen=True, но _MEIPASS отсутствует; файлы лежат рядом с exe
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(sys.executable)
    else:
        # Режим разработки: markdown_editor_pkg/ в проекте
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative)


def get_package_dir() -> str:
    """Возвращает путь к директории пакета markdown_editor_pkg.

    Работает как в режиме разработки, так и в собранном бинарнике.

    PyInstaller режимы:
    - onefile: sys._MEIPASS указывает на временную распакованную папку
    - onedir: sys.frozen=True, но _MEIPASS отсутствует; файлы лежат рядом с exe
    """
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            # onefile: распакованная временная директория
            return os.path.join(sys._MEIPASS, "markdown_editor_pkg")
        else:
            # onedir: файлы лежат рядом с исполняемым файлом
            return os.path.join(os.path.dirname(sys.executable), "markdown_editor_pkg")
    return os.path.dirname(os.path.abspath(__file__))


def get_base_dir() -> str:
    """Возвращает base_dir для рендеринга HTML.

    Это директория, где находятся prism/, mathjax/ и другие ресурсы,
    которые будут доступны через file:// URL в QWebEngineView.
    """
    return get_package_dir()
