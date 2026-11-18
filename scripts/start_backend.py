"""Inicia el backend Flask + Socket.IO del panel de administración (puerto 5000)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    print("Iniciando backend en http://localhost:5000 ...")
    subprocess.run([sys.executable, "server.py"], cwd=ROOT / "web_admin")
