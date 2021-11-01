# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from pyzbar import pyzbar
from os import makedirs
from shutil import copyfile

working_dir = 'C:\\Users\\saury\\Desktop\\Python Projects\\SmartScheduler\\smartscheduler'
block_cipher = None


a = Analysis(['smartscheduler\\gui.py'],
             pathex=[working_dir],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.binaries += TOC([
    (Path(dep._name).name, dep._name, 'BINARY') for dep in pyzbar.EXTERNAL_DEPENDENCIES
])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='SmartScheduler',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

makedirs('dist\\SmartScheduler\\remote_server', exist_ok=True)
copyfile(f'{working_dir}\\config.ini', 'dist\\SmartScheduler\\config.ini')
copyfile(f'{working_dir}\\remote_server\\subjects.csv', 'dist\\SmartScheduler\\remote_server\\subjects.csv')
copyfile(f'{working_dir}\\remote_server\\server.py', 'dist\\SmartScheduler\\remote_server\\server.csv')
