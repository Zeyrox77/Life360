# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for the Life360 Desktop application.

Produces a single windowed Windows executable (Life360.exe) that bundles the
FastAPI backend, the HTML/CSS/JS frontend and all runtime dependencies.

Build with:
    pyinstaller Life360.spec
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Bundle the frontend assets so the backend can serve them from inside the exe.
datas = [("frontend", "frontend"), ("assets", "assets")]
binaries = []
hiddenimports = []

# Packages whose data files / dynamic submodules PyInstaller cannot detect on
# its own. Wrapped in try/except so the spec also works where an optional,
# platform-specific package (e.g. pythonnet on non-Windows) is absent.
for package in (
    "curl_cffi",
    "uvicorn",
    "webview",
    "fastapi",
    "starlette",
    "pydantic",
    "pydantic_settings",
    "clr_loader",
    "pythonnet",
):
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
    except Exception:
        pass

hiddenimports += collect_submodules("uvicorn")
hiddenimports += [
    "webview.platforms.winforms",
    "webview.platforms.edgechromium",
]

block_cipher = None

a = Analysis(
    ["desktop.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Life360",
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
    icon="assets/Life360.ico",
)
