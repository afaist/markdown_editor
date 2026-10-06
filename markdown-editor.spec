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

# Collect ALL PyQt6 submodules and dynamic libraries
hiddenimports += collect_submodules('PyQt6')
datas += collect_data_files('PyQt6', subdir='')

# Collect all Qt6 data files (translations, plugins, etc.)
qt6_base = sysconfig.get_config_var('DESTLIBDIR')
if qt6_base:
    # Collect Qt plugins (platforms, webengine, etc.)
    for plugin_type in ['platforms', 'webengine_dtls', 'xcbglintegrations']:
        plugin_dir = os.path.join(qt6_base, 'PyQt6', 'Qt6', 'plugins', plugin_type)
        if os.path.isdir(plugin_dir):
            for f in os.listdir(plugin_dir):
                filepath = os.path.join(plugin_dir, f)
                if os.path.isfile(filepath):
                    binaries.append((filepath, os.path.join('PyQt6', 'Qt6', 'plugins', plugin_type)))

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


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    console=False,
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
