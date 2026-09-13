import os
import hashlib
import sqlite3

class FileIntegrityMonitor:
    """SI-GUARD Fayl Bütövlüyü Monitorinqi (FIM) Modulu"""
    def __init__(self, db_path="data/fim_baseline.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baseline (
                filepath TEXT PRIMARY KEY,
                hash TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _calculate_hash(self, filepath):
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return None

    def create_baseline(self, directory="."):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        count = 0
        
        for root, _, files in os.walk(directory):
            if any(ignored in root for ignored in ['.git', '__pycache__', 'data', 'node_modules', '.venv']):
                continue
            for file in files:
                filepath = os.path.normpath(os.path.join(root, file))
                file_hash = self._calculate_hash(filepath)
                if file_hash:
                    cursor.execute('''
                        INSERT INTO baseline (filepath, hash)
                        VALUES (?, ?)
                        ON CONFLICT(filepath) DO UPDATE SET hash=excluded.hash, updated_at=CURRENT_TIMESTAMP
                    ''', (filepath, file_hash))
                    count += 1
        
        conn.commit()
        conn.close()
        return f"📸 [FIM Baselines]: İlkin vəziyyət qeydə alındı! {count} fayl SHA-256 heşləndi və bazaya saxlanıldı."

    def check_integrity(self, directory="."):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT filepath, hash FROM baseline')
        baseline = dict(cursor.fetchall())
        conn.close()

        if not baseline:
            return "⚠️ Hələ ilkin vəziyyət (Baseline) yaradılmayıb. Əvvəlcə `fim baseline` əmrini icra edin."

        current_files = {}
        for root, _, files in os.walk(directory):
            if any(ignored in root for ignored in ['.git', '__pycache__', 'data', 'node_modules', '.venv']):
                continue
            for file in files:
                filepath = os.path.normpath(os.path.join(root, file))
                file_hash = self._calculate_hash(filepath)
                if file_hash:
                    current_files[filepath] = file_hash

        modified = []
        added = []
        deleted = []

        for path, h in current_files.items():
            if path not in baseline:
                added.append(path)
            elif baseline[path] != h:
                modified.append(path)

        for path in baseline:
            if path not in current_files:
                deleted.append(path)

        if not modified and not added and not deleted:
            return "✅ [FIM Auditi]: Sistemdə heç bir icazəsiz fayl dəyişikliyi aşkarlanmadı. Bütövlük tam qorunur!"

        report = "🚨 [FIM XƏBƏRDARLIĞI - Fayl Bütövlüyü Pozuntusu Aşkar Edildi!]:\n"
        if modified:
            report += f"  ⚠️ DƏYİŞDİRİLMİŞ FAYLLAR ({len(modified)}):\n" + "\n".join([f"   - {f}" for f in modified]) + "\n"
        if added:
            report += f"  ➕ YENİ ƏLAVƏ EDİLMİŞ FAYLLAR ({len(added)}):\n" + "\n".join([f"   - {f}" for f in added]) + "\n"
        if deleted:
            report += f"  🗑️ SİLİNMİŞ FAYLLAR ({len(deleted)}):\n" + "\n".join([f"   - {f}" for f in deleted]) + "\n"

        return report
