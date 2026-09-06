"""Сохранение и загрузка последней сессии (путь к последнему открытому файлу)."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SESSION_CONFIG_FILE = Path.home() / ".markdown_editor_config.json"


class SessionManager:
    """Сохраняет и восстанавливает путь к последнему открытому файлу.

    Данные хранятся в JSON-файле ~/.markdown_editor_config.json.
    """

    @staticmethod
    def save(filepath: str) -> None:
        """Сохранить путь к файлу в конфигурационном файле.

        Args:
            filepath: Абсолютный путь к файлу.
        """
        try:
            config = {"last_file": filepath}
            with open(SESSION_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f)
        except (OSError, json.JSONDecodeError):
            logger.exception("Ошибка при сохранении сессии")

    @staticmethod
    def load() -> str | None:
        """Загрузить путь к последнему файлу из конфигурации.

        Returns:
            Путь к последнему файлу или None, если не найден.
        """
        if not SESSION_CONFIG_FILE.exists():
            return None
        try:
            with open(SESSION_CONFIG_FILE, encoding="utf-8") as f:
                config = json.load(f)
            return str(config.get("last_file", "")) or None
        except (OSError, json.JSONDecodeError):
            return None
