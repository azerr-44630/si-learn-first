import os
import sqlite3

class KnowledgeBase:
    """SI-GUARD Anlama və Bilik Bazası Modulu"""
    def __init__(self, db_path="data/knowledge.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                content TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def ingest_file(self, file_path):
        if not os.path.exists(file_path):
            return f"❌ Fayl tapılmadı: {file_path}"

        ext = os.path.splitext(file_path)[1].lower()
        content = ""

        try:
            # Mətn əsaslı faylları oxu
            if ext in ['.txt', '.md', '.json', '.py', '.sh', '.log', '.env', '.html', '.css', '.js']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            # PDF faylları oxu
            elif ext == '.pdf':
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            content += extracted + "\n"
                except ImportError:
                    return "⚠️ PDF oxumaq üçün 'pypdf' paketi lazımdır. Yükləmək üçün: pip install pypdf"
            else:
                return f"⚠️ Dəstəklənməyən fayl formatı: {ext}"

            if not content.strip():
                return "⚠️ Fayl boşdur və ya mətni oxumaq mümkün olmadı."

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO knowledge (filename, content)
                VALUES (?, ?)
                ON CONFLICT(filename) DO UPDATE SET content=excluded.content, added_at=CURRENT_TIMESTAMP
            ''', (os.path.basename(file_path), content))
            conn.commit()
            conn.close()

            return f"🧠 [Anlama Modu]: `{os.path.basename(file_path)}` öyrənildi və bazaya daxil edildi ({len(content)} simvol)!"

        except Exception as e:
            return f"❌ Öyrənmə xətası: {str(e)}"

    def search_knowledge(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT filename, content FROM knowledge
            WHERE content LIKE ? OR filename LIKE ?
        ''', (f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()
        conn.close()

        if not results:
            return None

        context = "📚 [Yaddaşdan Alınan Bilik Context-i]:\n"
        for fname, cnt in results:
            context += f"\n--- Fayl: {fname} ---\n{cnt[:1500]}\n"
        return context

    def list_sources(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT filename, added_at FROM knowledge')
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "ℹ️ Bazada hələ heç bir öyrənilmiş fayl/mənbə yoxdur."

        res = "📚 [Öyrənilmiş Mənbələr Siyahısı]:\n"
        for r in rows:
            res += f" 📄 {r[0]} (Əlavə edilib: {r[1]})\n"
        return res
