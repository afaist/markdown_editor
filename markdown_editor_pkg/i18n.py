"""Internationalization (i18n) module using PyQt6 QTranslator.

Provides:
- setup_translator() — initialize QTranslator for the application
- load_language() — load a translation by language code
- get_available_languages() — list of supported languages
- tr() — convenience wrapper for QCoreApplication.translate("App", ...)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QCoreApplication, QLocale, QTranslator

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

# Directory where .qm translation files are stored.
# In development: <project_root>/locales/
# In PyInstaller:  <sys._MEIPASS>/locales/
_LOCALES_DIR: Path | None = None

# Global translator instance
_translator: QTranslator | None = None

# Available languages
_LANGUAGES: list[dict[str, str]] = [
    {"code": "en", "name": "English", "qm_file": "messages_en.qm"},
    {"code": "ru", "name": "Русский", "qm_file": "messages_ru.qm"},
]


def _locate_locales_dir() -> Path:
    """Return the absolute path to the locales/ directory."""
    global _LOCALES_DIR
    if _LOCALES_DIR is not None:
        return _LOCALES_DIR

    # PyInstaller frozen application
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        _LOCALES_DIR = Path(sys._MEIPASS) / "locales"
        return _LOCALES_DIR

    # Development: locate relative to this module
    package_dir = Path(__file__).resolve().parent
    candidate = package_dir.parent / "locales"
    if candidate.is_dir():
        _LOCALES_DIR = candidate
    else:
        # Fallback: locales might be at project root
        _LOCALES_DIR = candidate
    return _LOCALES_DIR


def setup_translator(app: QApplication) -> QTranslator:
    """Initialize and install the application translator.

    Loads the language from settings and installs the QTranslator on *app*.

    Returns:
        The QTranslator instance (installed on *app*).
    """
    global _translator

    _translator = QTranslator(app)
    locales_dir = _locate_locales_dir()

    # Determine preferred language from settings
    from markdown_editor_pkg.settings import Settings

    settings = Settings()
    lang_code = settings.get("language", "en")

    _load_translator(_translator, lang_code, locales_dir)
    app.installTranslator(_translator)

    logger.info("Translator initialized: language=%s", lang_code)
    return _translator


def load_language(lang_code: str) -> bool:
    """Reload the translator with a new language code.

    Call this after changing the language setting to apply the new
    translation at runtime. Widgets may need to be refreshed to show
    updated text.

    Args:
        lang_code: Language code, e.g. ``"en"`` or ``"ru"``.

    Returns:
        True if the translation file was loaded successfully.
    """
    global _translator

    if _translator is None:
        logger.warning("Translator not initialized; call setup_translator() first.")
        return False

    locales_dir = _locate_locales_dir()

    # Remove old translator from app
    app = QCoreApplication.instance()
    if app is not None and _translator is not None:
        app.removeTranslator(_translator)

    loaded = _load_translator(_translator, lang_code, locales_dir)
    if loaded and app is not None:
        app.installTranslator(_translator)

    logger.info("Language reloaded: language=%s", lang_code)
    return loaded


def _load_translator(
    translator: QTranslator, lang_code: str, locales_dir: Path
) -> bool:
    """Internal: load a .qm file for *lang_code* into *translator*."""
    lang_info = _get_language_info(lang_code)
    if lang_info is None:
        logger.warning("Unknown language code: %s", lang_code)
        return False

    qm_file = locales_dir / lang_info["qm_file"]
    if qm_file.exists():
        if translator.load(str(qm_file)):
            logger.info("Loaded translation: %s (%s)", lang_info["name"], qm_file)
            return True
        else:
            logger.error("Failed to load translation: %s", qm_file)
    else:
        logger.warning("Translation file not found: %s", qm_file)

    return False


def _get_language_info(code: str) -> dict[str, str] | None:
    """Return the language dict for *code*, or None."""
    for lang in _LANGUAGES:
        if lang["code"] == code:
            return lang
    return None


def get_available_languages() -> list[dict[str, str]]:
    """Return the list of available languages.

    Each entry is a dict with keys ``code``, ``name``, ``qm_file``.
    """
    return list(_LANGUAGES)


def tr(text: str) -> str:
    """Translate *text* using the ``App`` context.

    This is a convenience wrapper around
    ``QCoreApplication.translate("App", text)``. Use this function
    throughout the codebase to mark user-facing strings for translation.

    Args:
        text: The source-string (English) to translate.

    Returns:
        The translated string, or *text* itself if no translation is
        available.
    """
    return QCoreApplication.translate("App", text)


__all__ = [
    "get_available_languages",
    "load_language",
    "setup_translator",
    "tr",
]
