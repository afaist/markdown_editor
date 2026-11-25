"""Log cleaner — removes log files older than a specified number of days."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

LOG_DIR = Path.home() / ".local" / "share" / "markdown_editor"


def clean_old_logs(days: int = 7) -> int:
    """Удалить файлы логов старше указанного количества дней.

    Args:
        days: Количество дней хранения (по умолчанию 7).

    Returns:
        Количество удалённых файлов.
    """
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0

    try:
        if not LOG_DIR.exists():
            return 0

        for log_file in LOG_DIR.glob("markdown_editor_*.log"):
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff:
                    log_file.unlink()
                    deleted += 1
                    logger.debug("Deleted old log: %s", log_file.name)
            except OSError:
                pass
    except OSError:
        logger.debug("Could not access log directory: %s", LOG_DIR)

    if deleted:
        logger.info("Cleaned %d old log file(s) (older than %d days)", deleted, days)

    return deleted
