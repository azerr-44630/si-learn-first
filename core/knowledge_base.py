import sqlite3
import os

class KnowledgeBase:
    def __init__(self, db_path="knowledge.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Baza cədvəlini yaradır."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                threat_type TEXT,
                raw_log TEXT,
                vt_malicious INTEGER,
                blocked INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    def log_threat(self, ip, threat_type, raw_log, vt_malicious=0, blocked=0):
        """Hücum məlumatını bazaya daxil edir."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO threats (ip, threat_type, raw_log, vt_malicious, blocked)
            VALUES (?, ?, ?, ?, ?)
        ''', (ip, threat_type, raw_log, vt_malicious, blocked))
        conn.commit()
        conn.close()
