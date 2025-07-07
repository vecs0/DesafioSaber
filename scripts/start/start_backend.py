import subprocess
import sys
import os
 
if __name__ == "__main__":
    print("Iniciando backend Flask (servidor de administración)...")
    os.chdir("web_admin")
    subprocess.run([sys.executable, "server.py"]) 