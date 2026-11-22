"""Runtime hook: set Qt platform plugin path for PyInstaller bundles."""

import os
import sys

if getattr(sys, "frozen", False):
    if hasattr(sys, "_MEIPASS"):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(sys.executable)

    # Try both Qt6/ (>= 6.8) and Qt/ (<= 6.7)
    for qt_dir_name in ("Qt6", "Qt"):
        plugin_path = os.path.join(bundle_dir, "PyQt6", qt_dir_name, "plugins")
        if os.path.isdir(plugin_path):
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
            # Force Windows platform plugin on Windows
            if sys.platform == "win32":
                os.environ["QT_QPA_PLATFORM"] = "windows"
            break
