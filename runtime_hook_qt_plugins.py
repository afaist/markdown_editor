"""Runtime hook: set Qt platform plugin path for PyInstaller bundles."""

import os
import sys

# In PyInstaller bundle, PyQt6 is collected with its Qt subdirectory.
# Qt dir name changed from Qt/ to Qt6/ in PyQt6 >= 6.8.
if getattr(sys, "frozen", False):
    if hasattr(sys, "_MEIPASS"):
        # onefile mode: temp extract dir
        bundle_dir = sys._MEIPASS
    else:
        # onedir (COLLECT) mode: exe is inside dist/markdown-editor/
        bundle_dir = os.path.dirname(sys.executable)

    # Try both Qt6/ (>= 6.8) and Qt/ (<= 6.7)
    for qt_dir_name in ('Qt6', 'Qt'):
        plugin_path = os.path.join(bundle_dir, 'PyQt6', qt_dir_name, 'plugins')
        if os.path.isdir(plugin_path):
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
            break
