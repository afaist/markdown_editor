# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
import sysconfig
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebChannel', 'markdown', 'markdown.extensions.fenced_code', 'markdown.extensions.tables', 'markdown.extensions.toc']
tmp_ret = collect_all('markdown_editor_pkg')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

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
