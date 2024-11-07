# pydeilabs-mac.spec

from PyInstaller.utils.hooks import collect_data_files


# Define the main script and build parameters
a = Analysis(
    ['pydeilabs.py'],           # Your main script
    pathex=['.'],                # Paths to search
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=None
)

# Python bytecode zip
pyz = PYZ(a.pure)

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
        console=False,          # Set to True if you want console output
        icon='pydeilabs.icns'   # Icon file for macOS
)

# Create a BUNDLE to package as a macOS .app file
app = BUNDLE(
    exe,
    name='pydeilabs.app',
    icon='deilabs.icns',       # Icon for the app bundle
    bundle_identifier='com.example.pydeilabs'
)

