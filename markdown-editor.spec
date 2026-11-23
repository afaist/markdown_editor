# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
import sysconfig
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

datas = []
binaries = []
hiddenimports = [
    'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebChannel', 'PyQt6.QtNetwork', 'PyQt6.QtOpenGL',
    'markdown', 'markdown.extensions.fenced_code',
    'markdown.extensions.tables', 'markdown.extensions.toc',
]

# Collect all markdown_editor_pkg files
tmp_ret = collect_all('markdown_editor_pkg')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Collect prism/ and mathjax/ as data files (not Python packages)
for root, dirs, files in os.walk('markdown_editor_pkg/prism'):
    for f in files:
        src = os.path.join(root, f)
        dst = os.path.relpath(os.path.dirname(src), 'markdown_editor_pkg')
        datas.append((src, os.path.join('markdown_editor_pkg', dst)))

for root, dirs, files in os.walk('markdown_editor_pkg/mathjax'):
    for f in files:
        src = os.path.join(root, f)
        dst = os.path.relpath(os.path.dirname(src), 'markdown_editor_pkg')
        datas.append((src, os.path.join('markdown_editor_pkg', dst)))

# Collect ALL PyQt6 files (submodules + binaries including Qt plugins)
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# collect_all('PyQt6') only processes the PyQt6/ Python package.
# The Qt binaries (plugins, icudtl.dat, Qt6Core.dll, etc.) live in
# a sibling directory — name changed from Qt/ to Qt6/ in PyQt6 >= 6.8.
import importlib.util
_pyqt6_spec = importlib.util.find_spec('PyQt6')
_pyqt6_base = os.path.dirname(_pyqt6_spec.origin) if _pyqt6_spec else None
if _pyqt6_base:
    for qt_dir_name in ('Qt6', 'Qt'):
        qt_base = os.path.join(_pyqt6_base, qt_dir_name)
        if os.path.isdir(qt_base):
            # Walk all subdirectories (plugins, lib, bin, translations, etc.)
            for root, dirs, files in os.walk(qt_base):
                for f in files:
                    src = os.path.join(root, f)
                    rel = os.path.relpath(src, _pyqt6_base)
                    dst = os.path.join('PyQt6', qt_dir_name, os.path.dirname(rel))
                    if f.endswith(('.dll', '.exe', '.so', '.dylib', '.a')):
                        binaries.append((src, dst))
                    else:
                        datas.append((src, dst))
            break  # only one of Qt/ or Qt6/ exists

# Include libpython shared library (required when building with pyenv)
libpython = sysconfig.get_config_var('LIBPL')
if libpython:
    for f in os.listdir(libpython):
        if f.startswith('libpython') and (f.endswith('.so') or f.endswith('.so.1.0')):
            binaries.append((os.path.join(libpython, f), '.'))

# Include translation files
locales_dir = Path("locales")
if locales_dir.is_dir():
    for qm in locales_dir.glob("*.qm"):
        datas.append((str(qm), "locales"))

# Include runtime hooks
runtime_hooks = [
    str(Path("runtime_hook_gio.py")),
    str(Path("runtime_hook_qt_plugins.py")),
]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks,
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='markdown-editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='markdown-editor',
)
