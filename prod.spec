# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_production.py'],
    pathex=[],
    binaries=[],
    datas=[('DoorsAndDrawers', 'DoorsAndDrawers'), ('db.sqlite3', '.'), ('staticfiles', 'staticfiles'), ('templates', 'templates')],
    hiddenimports=['whitenoise.middleware', 'whitenoise', 'encodings'],
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
    name='run_production',
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
    name='run_production',
)
