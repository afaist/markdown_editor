#!/usr/bin/env python3
"""
Markdown Editor - A simple Markdown editor with preview and LaTeX support.
"""

import json
import os
import sys
from pathlib import Path

# ── GPU acceleration (must be set before any Qt import) ──────────────────

_config_path = Path.home() / ".markdown_editor_config.json"
_disable_gpu = False

if _config_path.exists():
    try:
        with open(_config_path, encoding="utf-8") as f:
            _cfg = json.load(f)
        _disable_gpu = bool(_cfg.get("disable_gpu", False))
    except (json.JSONDecodeError, OSError):
        pass

_chromium_flags = "--log-level=3"

if _disable_gpu:
    _chromium_flags += (
        " --disable-gpu --disable-gpu-compositing --disable-software-rasterizer"
        " --disable-gpu-info-update"
    )
    os.environ["QTWEBENGINE_SETTINGS"] = '{"enable_gpu": "false"}'

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = _chromium_flags
os.environ["QT_LOGGING_RULES"] = "qt.webengine.services=false"

# ── Suppress Chromium/Mesa stderr messages (GBM, GPUInfo, etc.) ──────────
# These messages come from Mesa/Chromium directly to stderr, not via Qt.
# Redirect stderr to /dev/null before QApplication initialization,
# then restore it after the app is created so Python errors are visible.

_stderr_backup = None

if os.name == "posix":
    _devnull_fd = os.open(os.devnull, os.O_WRONLY)
    _stderr_backup = os.dup(2)
    os.dup2(_devnull_fd, 2)
    os.close(_devnull_fd)

from PyQt6.QtWidgets import QApplication

from markdown_editor_pkg import __version__
from markdown_editor_pkg.editor import MarkdownEditorPyQt
from markdown_editor_pkg.i18n import setup_translator


def main() -> None:
    """Main application entry point."""
    # Restore stderr after Qt initialization so Python errors are visible
    global _stderr_backup
    if _stderr_backup is not None:
        os.dup2(_stderr_backup, 2)
        os.close(_stderr_backup)
        _stderr_backup = None

    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Editor")
    app.setApplicationVersion(__version__)
    setup_translator(app)
    window = MarkdownEditorPyQt()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
