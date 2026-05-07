# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = []
datas += collect_data_files('qfluentwidgets')
datas += collect_data_files('PyQt6')
datas += collect_data_files('PyQt6_Qt6')
datas += [(r'E:\Python code\taskmanager\aura_tasks_pro\resources', 'aura_tasks_pro/resources')]

hiddenimports = []
hiddenimports += collect_submodules('qfluentwidgets')
hiddenimports += collect_submodules('PyQt6')
hiddenimports += collect_submodules('PyQt6_Qt6')
hiddenimports += collect_submodules('PyQt6_sip')
hiddenimports += collect_submodules('PyQt6_Frameless_Window')

a = Analysis(
    [r'E:\Python code\taskmanager\run.py'],
    pathex=[r'E:\Python code\taskmanager'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AuraTasksPro',
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
    icon=r'E:\Python code\taskmanager\aura_tasks_pro\resources\app_icon.ico',
)
