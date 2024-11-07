# pydeilabs-win.spec

# Importing the required modules from PyInstaller
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.__main__ import Analysis, PYZ, EXE, COLLECT


# Define the main script and build parameters
a = Analysis(
    ['pydeilabs.py'],           # Your main script
    pathex=['.'],                # Paths to search
    binaries=[],
    datas=[('/config', '/config')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)

# Python bytecode zip
pyz = PYZ(a.pure)

# EXE target with icon and specific output name
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pydeilabs',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,              # Set to True if you want console output
    icon='pydeilabs.ico'        # Icon file for Windows
)

# COLLECT creates the single-file output
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='dist')
