# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ns2/main.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/jowens/Projects/ns2/.venv/lib/python3.12/site-packages/nicegui', 'nicegui'), ('ns2/assets', 'ns2/assets'), ('ns2/introspection', 'ns2/introspection')],
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
    [],
    exclude_binaries=True,
    name='ns2',
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
    name='ns2',
)
