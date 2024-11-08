# pydeilabs-linux.spec

from PyInstaller.utils.hooks import collect_data_files

# Collect data files if needed
datas = collect_data_files("pydeilabs")

# Define the main script and build parameters
a = Analysis(
    ['pydeilabs.py'],           # Your main script
    pathex=['.'],                # Paths to search
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=None
)

# Python bytecode zip
pyz = PYZ(a.pure)

# EXE target for Linux with no icon
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
    console=False  # Set to True if you want console output
)

# COLLECT creates the single-file output
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='dist')
