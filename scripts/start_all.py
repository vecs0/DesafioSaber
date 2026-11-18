"""Inicia el sistema completo de DesafíoSaber.

1. Backend Flask + Socket.IO  -> http://localhost:5000
2. Panel de administración    -> http://localhost:3000
3. Juego de escritorio (Tkinter)

Al cerrar el juego se detienen el backend y el panel.
Uso:  python scripts/start_all.py [--sin-panel]
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NPM = "npm.cmd" if os.name == "nt" else "npm"


def main():
    procesos = []
    try:
        print("▶ Backend:  http://localhost:5000")
        procesos.append(subprocess.Popen([sys.executable, "server.py"], cwd=ROOT / "web_admin"))

        if "--sin-panel" not in sys.argv:
            web = ROOT / "web_admin"
            if not (web / "node_modules").exists():
                print("Instalando dependencias del panel (npm install)...")
                subprocess.run([NPM, "install"], cwd=web, check=True)
            print("▶ Panel:    http://localhost:3000")
            procesos.append(subprocess.Popen([NPM, "start"], cwd=web))

        time.sleep(3)
        print("▶ Juego de escritorio")
        subprocess.run([sys.executable, str(ROOT / "game" / "main.py")], cwd=ROOT)
    except KeyboardInterrupt:
        pass
    finally:
        print("Cerrando servicios...")
        for p in procesos:
            p.terminate()


if __name__ == "__main__":
    main()
