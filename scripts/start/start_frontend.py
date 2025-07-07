import subprocess
import os
import sys

if __name__ == "__main__":
    print("Iniciando frontend React (panel de administración)...")
    os.chdir("web_admin")
    npm_command = "npm.cmd" if os.name == "nt" else "npm"
    subprocess.run([npm_command, "start"]) 