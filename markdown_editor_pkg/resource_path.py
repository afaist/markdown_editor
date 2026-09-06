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
    # PyInstaller создаёт временную папку и помещает туда все ресурсы
    # sys._MEIPASS указывает на эту папку только в собранном приложении
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # Режим разработки: markdown_editor_pkg/ в проекте
        package_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = package_dir

    return os.path.join(base_path, relative)


def get_package_dir() -> str:
    """Возвращает путь к директории пакета markdown_editor_pkg.

    Работает как в режиме разработки, так и в собранном бинарнике.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return str(sys._MEIPASS)  # type: ignore[no-any-return]
    return os.path.dirname(os.path.abspath(__file__))


def get_base_dir() -> str:
    """Возвращает base_dir для рендеринга HTML.

    Это директория, где находятся katex/, prism/ и другие ресурсы,
    которые будут доступны через file:// URL в QWebEngineView.
    """
    return get_package_dir()
