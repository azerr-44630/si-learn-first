import sqlite3
import os

class KnowledgeBase:
    def __init__(self):
        self.db_path = 'data/knowledge.db'
        os.makedirs('data', exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.setup_tables()

    def setup_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
