"""Genera el ejecutable de Windows del juego y el .zip para el GitHub Release.

Requisitos:  pip install -r requirements-dev.txt
Uso:         python scripts/build_exe.py

Resultado:   release/DesafioSaber-v<versión>-windows.zip
             (carpeta con DesafioSaber.exe + data/ + assets/)
"""
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

VERSION = "1.1.0"
ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
DIST = ROOT / "dist"
RELEASE = ROOT / "release"
NOMBRE = "DesafioSaber"

# Archivos de datos que se distribuyen (sin historial ni sesiones locales)
DATOS_EXCLUIDOS = {"current_user.json", "current_duel.json", "offline_queue.json"}


def main():
    BUILD.mkdir(exist_ok=True)
    icono = BUILD / "icono.ico"
    Image.open(ROOT / "assets" / "images" / "logo.png").save(
        icono, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )

    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--clean", "--windowed",
            "--name", NOMBRE,
            "--icon", str(icono),
            "--paths", str(ROOT / "game"),
            "--distpath", str(DIST),
            "--workpath", str(BUILD / "pyinstaller"),
            "--specpath", str(BUILD),
            str(ROOT / "game" / "main.py"),
        ],
        check=True,
        cwd=ROOT,
    )

    destino = DIST / NOMBRE
    shutil.copytree(ROOT / "assets", destino / "assets", dirs_exist_ok=True)
    (destino / "data").mkdir(exist_ok=True)
    for archivo in (ROOT / "data").glob("*.json"):
        if archivo.name not in DATOS_EXCLUIDOS:
            shutil.copy2(archivo, destino / "data" / archivo.name)
    shutil.copy2(ROOT / "LICENSE", destino / "LICENSE.txt")

    RELEASE.mkdir(exist_ok=True)
    base = RELEASE / f"{NOMBRE}-v{VERSION}-windows"
    zip_path = shutil.make_archive(str(base), "zip", DIST, NOMBRE)
    print(f"\nListo: {zip_path}")


if __name__ == "__main__":
    main()
