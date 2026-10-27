# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

sys.path.insert(0, str(Path("src").resolve()))

a = Analysis(
    ['src/webapp/__init__.py'],
    pathex=["src"],
    binaries=[],
    datas=[
        ("src/webapp/pages", "pages"),
        ("assets", "assets"),
    ],
    hiddenimports=collect_submodules("webapp"),
    hookspath=['src/webapp/hooks'],
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
    a.binaries,
    a.datas,
    [],
    name='tracker',
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
