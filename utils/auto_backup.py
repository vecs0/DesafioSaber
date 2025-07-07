import os
import shutil
from datetime import datetime

def auto_backup(file_path, backup_dir="backups"):
    """
    Realiza una copia de seguridad del archivo especificado en el directorio de backups con timestamp.
    """
    if not os.path.exists(file_path):
        return False
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    base = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{base}_backup_{timestamp}.json"
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(file_path, backup_path)
    return backup_path 