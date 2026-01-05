# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

# HTML
datas += [('app_frontend.html', '.')]

# backend python
datas += [('app_backend.py', '.')]

# pywebview / fastapi / uvicorn まわりを収集
for pkg in ['webview', 'fastapi', 'uvicorn', 'starlette', 'pydantic']:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
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
    [],
    exclude_binaries=True,
    name='JPG Move Tool',
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='JPG Move Tool',
)

app = BUNDLE(
    coll,
    name='JPG Move Tool.app',
    info_plist={
        "LSUIElement": False,  # Dockに表示
        "CFBundleName": "JPG Move Tool",
        "CFBundleDisplayName": "JPG Move Tool",
    },
)
