# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['prod.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('DoorsAndDrawers', 'DoorsAndDrawers'),
        ('core', 'core'),
        ('db.sqlite3', '.'),
        ('staticfiles', 'staticfiles'),
        ('templates', 'templates')
    ],
    hiddenimports=[
        'whitenoise',
        'whitenoise.middleware',
        'encodings',
        'django.contrib.staticfiles.templatetags.staticfiles',
        'django.contrib.messages.templatetags.messages',
        'django_htmx.context_processors',
        'reportlab.graphics.barcode.code128',
    	'reportlab.graphics.barcode.code39',
        'reportlab.graphics.barcode.code93',
        'reportlab.graphics.barcode.usps4s',
        'reportlab.graphics.barcode.ecc200datamatrix',
    	'reportlab.graphics.barcode.usps',
    ],
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
