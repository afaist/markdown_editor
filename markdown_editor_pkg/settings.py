"""Centralized settings manager — JSON-backed persistence.

Replaces the minimal ``session_manager`` with a full settings store
that keeps ``language``, ``theme``, ``editor_font``, ``editor_font_size``,
and the legacy ``last_file`` key.

Usage::

    from markdown_editor_pkg.settings import Settings

    settings = Settings()
    lang = settings.get("language", "en")
    settings.set("language", "ru")
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONFIG_FILE: Path = Path.home() / ".markdown_editor_config.json"

# Default values for all known settings
DEFAULTS: dict[str, Any] = {
    "language": "en",
    "theme": "light",
    "editor_theme": "light",
    "editor_font": "Consolas",
    "editor_font_size": 11,
    "last_file": "",
}


class Settings:
    """Thin JSON-backed settings store.

    All values are read from disk once (on first ``get``/``set``) and
    cached in memory.  Changes are written back to disk immediately.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """Инициализация менеджера настроек.

        Args:
            config_path: Путь к файлу конфигурации; по умолчанию ~/.markdown_editor_config.json.
        """
        self._path: Path = config_path or CONFIG_FILE
        self._data: dict[str, Any] = dict(DEFAULTS)
        self._loaded = False

    # ── Public API ────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение настройки по ключу с fallback на default.

        Args:
            key: Ключ настройки.
            default: Значение по умолчанию, если ключ отсутствует.

        Returns:
            Значение настройки или default.
        """
        self._ensure_loaded()
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Установить значение настройки и сохранить на диск.

        Args:
            key: Ключ настройки.
            value: Новое значение.
        """
        self._ensure_loaded()
        self._data[key] = value
        self._persist()

    def get_all(self) -> dict[str, Any]:
        """Возвращает копию всех настроек.

        Returns:
            Словарь со всеми текущими настройками.
        """
        self._ensure_loaded()
        return dict(self._data)

    # ── Internal ──────────────────────────────────────────────────────

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        if not self._path.exists():
            logger.debug("No config file found; using defaults.")
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._data.update(data)
            logger.debug("Loaded settings from %s", self._path)
        except (OSError, json.JSONDecodeError):
            logger.exception("Failed to load settings from %s", self._path)

    def _persist(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except OSError:
            logger.exception("Failed to save settings to %s", self._path)
