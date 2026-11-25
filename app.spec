# Fabrication de l'exe avec PyInstaller (lancer build_exe.bat, ou voir le README).
# Le nom de l'exe et l'icône viennent de backend/app_info.py et du dossier icone/ : rien à changer ici.
import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

sys.path.insert(0, os.path.join(SPECPATH, "backend"))
from app_info import APP_NAME, EXE_NAME  # noqa: E402

VERSION = Path(SPECPATH, "VERSION").read_text(encoding="utf-8").strip()
try:  # version affichée dans Propriétés › Détails de l'exe (modules Windows de PyInstaller)
    from PyInstaller.utils.win32.versioninfo import (
        FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo,
    )
except ImportError:
    version_info = None
else:
    _numeros = tuple(int(p) for p in VERSION.split("-")[0].split(".")) + (0,)
    version_info = VSVersionInfo(
        ffi=FixedFileInfo(filevers=_numeros[:4], prodvers=_numeros[:4]),
        kids=[
            StringFileInfo([StringTable("040C04B0", [
                StringStruct("ProductName", APP_NAME),
                StringStruct("FileDescription", APP_NAME),
                StringStruct("ProductVersion", VERSION),
                StringStruct("FileVersion", VERSION),
                StringStruct("OriginalFilename", f"{EXE_NAME}.exe"),
            ])]),
            VarFileInfo([VarStruct("Translation", [0x040C, 1200])]),
        ],
    )

a = Analysis(
    [os.path.join(SPECPATH, "backend", "launcher.py")],
    pathex=[os.path.join(SPECPATH, "backend")],
    datas=[(os.path.join(SPECPATH, "frontend", "dist"), "interface"), (os.path.join(SPECPATH, "VERSION"), ".")],
    hiddenimports=collect_submodules("uvicorn"),
    excludes=["tkinter", "matplotlib", "IPython", "numpy", "pandas"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=EXE_NAME,
    icon=os.path.join(SPECPATH, "icone", "app.ico"),
    version=version_info,
    console=True,
    upx=False,
)
