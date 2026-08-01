# -*- mode: python ; coding: utf-8 -*-
import os
import tkinterdnd2

dnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

a = Analysis(
    ['spiramm.py'],
    pathex=[],
    binaries=[],
    datas=[(dnd_path, 'tkinterdnd2/tkdnd'), ('SpiraMM.ico', '.')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='SpiraModManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='spiramm_version.txt',
    icon='SpiraMM.ico',
)
