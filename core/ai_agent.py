import sqlite3
import re

class AIAgent:
    def __init__(self, db, blocker):
        self.db = db
        self.blocker = blocker

    def process_command(self, user_input):
        command = user_input.lower().strip()

        # 1. Nəzakət və Hal-Əhval Sorğuları
        if any(w in command for w in ["salam", "salamlar", "hello", "hi"]):
            return (
                "🤖 SI: Salam! Mən avtonom Blue Team müdafiə agentinizəm.\n"
                "   Canlı logları izləyir və zərərli IP-ləri bloklayıram. Sizə necə kömək edə bilərəm?"
            )
        elif any(w in command for w in ["necesen", "neceksen", "necəsən", "ne var ne yox", "nə var nə yox"]):
            return "🤖 SI: Mən bir AI agentəm, sistem resurslarım tam qaydasındadır və canlı izləmədəyəm! Sizdə vəziyyət necədir?"

        # 2. Sistem İş Prinsipi / İzahlar
        elif any(w in command for w in ["nece etdin", "necə etdin", "nece isleyir", "necə işləyir", "nece tutdun", "necə tutdun", "haqqinda"]):
            return (
                "🔍 SI İş Prinsipi:\n"
                "  1. LogMonitor: Web serverin 'access.log' faylını real-vaxtda oxuyur.\n"
                "  2. PayloadAnalyzer: Regex vasitəsilə SQLi, XSS və zərərli parametrləri tapır.\n"
                "  3. ThreatIntel & Blocker: VirusTotal reputasiyasını yoxlayıb IP-ni 'iptables' vasitəsilə bloklayır.\n"
                "  4. KnowledgeBase: Bütün bu prosesləri SQLite bazasında arxivləyir."
            )

        # 3. Sistem Vəziyyəti / Status
        elif any(w in command for w in ["status", "veziyyet", "vəziyyət", "sistem", "isleyir", "işləyir"]):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM threats")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM threats WHERE blocked=1")
            blocked = cursor.fetchone()[0]
            conn.close()
            return (
                f"📊 SI Sistem Hesabatı:\n"
                f"  • Log Monitorinqi: Aktiv 🟢\n"
                f"  • Qeydə alınan hücumlar: {total}\n"
                f"  • Bloklanan IP-lər: {blocked}\n"
                f"  • Bazanın vəziyyəti: Qaydasındadır"
            )

        # 4. Hücumların Və Logların Siyahısı
        elif any(w in command for w in ["hucum", "hücum", "tehdid", "təhdid", "log", "siyahı", "siyahi", "son", "baxim", "baxım"]):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT ip, threat_type, timestamp, blocked FROM threats ORDER BY id DESC LIMIT 5")
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return "🤖 SI: Bazada hələ ki heç bir təhdid qeydə alınmayıb. Server təmizdir!"
            
            res = "🚨 SI: Son aşkar edilən hücumlar:\n"
            for r in rows:
                status = "🛡️ Bloklandı" if r[3] == 1 else "⚠️ Təsbit edildi"
                res += f"  • [{r[2]}] IP: {r[0]} | Növ: {r[1]} | Status: {status}\n"
            return res

        # 5. Dinamik IP Bloklama Əmri
        elif any(w in command for w in ["blokla", "block", "ban", "qadağan"]):
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', command)
            if ip_match:
                ip = ip_match.group(1)
                self.blocker.block_ip(ip)
                return f"🛡️ SI: {ip} ünvanı dərhal müdafiə sisteminə ötürüldü və bloklandı."
            return "⚠️ SI: Əmrdə keçərli bir IP ünvanı tapılmadı (Məsələn: '1.2.3.4 IP-ni blokla')."

        # 6. Kömək / Təlimat
        elif any(w in command for w in ["komek", "kömək", "help", "ne ede bilersen", "nə edə bilərsən"]):
            return (
                "💡 SI Agent İdarəetmə Komandaları:\n"
                "  1. 'salam' / 'necesen' - Agent ilə əlaqə qurmaq\n"
                "  2. 'status' / 'necə etdin' - Sistem vəziyyəti və iş prinsipi\n"
                "  3. 'hücumlar' - Son aşkar edilən təhdidlər\n"
                "  4. '<IP> blokla' - Göstərilən IP-ni dərhal firewall-a əlavə etmək\n"
                "  5. 'exit' - Çat rejimindən çıxmaq"
            )

        # Standart Cavab
        else:
            return (
                "🤖 SI: Bu əmri tam anlayamadım. Mənimlə nəzakətlə danışa, 'status' və ya 'hücumlar' sorğulaya,\n"
                "   yaxud da 'necə etdin' yazaraq iş prinsipimi öyrənə bilərsiniz. Təlimat üçün 'kömək' yazın."
            )
