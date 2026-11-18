"""Rutas del proyecto.

Resuelve la carpeta raíz tanto al ejecutar desde el código fuente como desde
el ejecutable generado con PyInstaller, y fija el directorio de trabajo en la
raíz para que las rutas relativas (``data/...``, ``assets/...``) funcionen
sin importar desde dónde se lance el juego.
"""
import os
import sys

# Los mensajes del juego usan emojis: evitar UnicodeEncodeError en consolas
# de Windows que no están en UTF-8 (cp1252).
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

if getattr(sys, "frozen", False):
    # Ejecutable: data/ y assets/ se distribuyen junto al .exe
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(ROOT_DIR, "data")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

os.chdir(ROOT_DIR)
