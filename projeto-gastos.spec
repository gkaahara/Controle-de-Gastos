# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\runner.py'],
    pathex=[],
    binaries=[],
    datas=[('app/templates', 'app/templates'), ('app/static', 'app/static')],
    hiddenimports=['flask', 'portalocker', 'app', 'app.routes', 'app.routes.main', 'app.routes.categorias', 'app.routes.salarios', 'app.routes.gastos_casa', 'app.routes.cartoes', 'app.routes.relatorios', 'app.routes.dashboard'],
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
    a.binaries,
    a.datas,
    [],
    name='projeto-gastos',
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
)
