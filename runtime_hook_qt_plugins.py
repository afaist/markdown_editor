"""Runtime hook: set Qt platform plugin path for PyInstaller bundles."""

import os
import sys

# In PyInstaller bundle, PyQt6 is collected with its Qt subdirectory.
# The structure is: bundle_dir/PyQt6/Qt/plugins/
if getattr(sys, "frozen", False):
    if hasattr(sys, "_MEIPASS"):
        # onefile mode: temp extract dir
        plugin_path = os.path.join(sys._MEIPASS, "PyQt6", "Qt", "plugins")
    else:
        # onedir (COLLECT) mode: exe is inside dist/markdown-editor/
        bundle_dir = os.path.dirname(sys.executable)
        plugin_path = os.path.join(bundle_dir, "PyQt6", "Qt", "plugins")

    if os.path.isdir(plugin_path):
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
