import os
import tarfile
import json
import shutil
from datetime import datetime

class BrainBackup:
    def __init__(self, backup_dir='backups'):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(self.backup_dir, f'backup_{timestamp}.tar.gz')
        with tarfile.open(filepath, "w:gz") as tar:
            if os.path.exists('data'):
                tar.add('data', arcname='data')
        return filepath
