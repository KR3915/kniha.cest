# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['login_screen.py'],  # Hlavní spouštěcí soubor
    pathex=[],
    binaries=[],
    datas=[
        ('assets/principal_logo.png', 'assets'),  # Logo
        ('database.db', '.'),  # Databázový soubor
    ],
    hiddenimports=[
        'customtkinter',
        'tkcalendar',
        'openpyxl',
        'requests',
        'json',
        'datetime',
        'math',
        'random',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Kniha.cest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False pro aplikaci bez konzole
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/principal_logo.ico'  # Ikona aplikace
) 