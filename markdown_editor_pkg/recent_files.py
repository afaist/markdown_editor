"""Менеджер списка недавно открытых файлов (Recent Files).

Хранит список последних открытых файлов в Settings.
Максимальное количество записей регулируется константой MAX_RECENT.
"""

from __future__ import annotations

import logging
from pathlib import Path

from markdown_editor_pkg.settings import Settings

logger = logging.getLogger(__name__)

MAX_RECENT: int = 10
RECENT_KEY: str = "recent_files"


class RecentFilesManager:
    """Управление списком недавно открытых файлов.

    Список сохраняется в JSON-конфиге и ограничивается MAX_RECENT записями.
    """

    def __init__(self) -> None:
        self._settings = Settings()
        self._recent: list[str] = []
        self._load()

    # ── Public API ────────────────────────────────────────────────────

    def add(self, filepath: str) -> None:
        """Добавить файл в список недавно открытых.

        Если файл уже есть — перемещает его в начало списка.

        Args:
            filepath: Путь к файлу.
        """
        if not filepath:
            return

        # Убрать дубликат, если есть
        if filepath in self._recent:
            self._recent.remove(filepath)

        self._recent.insert(0, filepath)

        # Ограничить длину
        if len(self._recent) > MAX_RECENT:
            self._recent = self._recent[:MAX_RECENT]

        self._persist()

    def get(self) -> list[str]:
        """Возвращает список недавно открытых файлов.

        Returns:
            Список путей, от newest к oldest.
        """
        # Фильтруем: убираем несуществующие файлы
        self._recent = [f for f in self._recent if Path(f).exists()]
        return self._recent

    def clear(self) -> None:
        """Очищает список недавно открытых файлов."""
        self._recent = []
        self._persist()

    def remove(self, filepath: str) -> None:
        """Удаляет конкретный файл из списка."""
        if filepath in self._recent:
            self._recent.remove(filepath)
            self._persist()

    # ── Internal ──────────────────────────────────────────────────────

    def _load(self) -> None:
        """Загружает список из Settings."""
        try:
            data = self._settings.get(RECENT_KEY, [])
            if isinstance(data, list):
                self._recent = [str(p) for p in data if p]
        except Exception:
            logger.exception("Failed to load recent files")
            self._recent = []

    def _persist(self) -> None:
        """Сохраняет список в Settings."""
        try:
            self._settings.set(RECENT_KEY, self._recent)
        except Exception:
            logger.exception("Failed to save recent files")
