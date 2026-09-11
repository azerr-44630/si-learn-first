import sqlite3

class AIAgent:
    def __init__(self, db, blocker):
        self.db = db
        self.blocker = blocker

    def process_command(self, user_input):
        """İstifadəçinin təbii dildə verdiyi əmri emal edir."""
        command = user_input.lower().strip()

        # 1. Təhdidləri/Logları sorğulamaq
        if "hücum" in command or "təhdid" in command or "log" in command:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT ip, threat_type, timestamp FROM threats ORDER BY id DESC LIMIT 5")
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return "🤖 AI: Bazada hələ ki heç bir hücum qeydə alınmayıb."
            
            res = "🤖 AI: Son qeydə alınan hücumlar:\n"
            for r in rows:
                res += f"  • [{r[2]}] IP: {r[0]} | Növ: {r[1]}\n"
            return res

        # 2. IP Bloklama əmri
        elif "blokla" in command or "ban" in command:
            words = command.split()
            for word in words:
                # Sadə IP tapma məntiqli
                if word.count('.') == 3:
                    self.blocker.block_ip(word)
                    return f"🤖 AI: {word} ünvanı dərhal blok siyahısına əlavə edildi."
            return "🤖 AI: Bloklamaq üçün keçərli bir IP ünvanı tapılmadı."

        # 3. Status/Statistika
        elif "status" in command or "statistika" in command:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM threats")
            total = cursor.fetchone()[0]
            conn.close()
            return f"🤖 AI: Sistem aktivdir. Ümumi təsbit edilən hücum sayı: {total}"

        else:
            return "🤖 AI: Əmrinizi anlamadım. Nümunə əmrlər: 'son hücumları göstər', '45.33.32.156 IP-ni blokla', 'statistika'"
