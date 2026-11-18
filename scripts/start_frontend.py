"""Inicia el panel de administración en React (puerto 3000)."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NPM = "npm.cmd" if os.name == "nt" else "npm"

if __name__ == "__main__":
    web = ROOT / "web_admin"
    if not (web / "node_modules").exists():
        print("Instalando dependencias del panel (npm install)...")
        subprocess.run([NPM, "install"], cwd=web, check=True)
    print("Iniciando panel en http://localhost:3000 ...")
    subprocess.run([NPM, "start"], cwd=web)
