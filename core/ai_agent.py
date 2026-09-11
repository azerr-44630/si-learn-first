import re

class AIAgent:
    def __init__(self, db, blocker):
        self.db = db
        self.blocker = blocker
        self.last_target_ip = None  # Sonuncu əlaqəli IP-ni yadda saxlayır

    def process_command(self, command):
        cmd = command.lower().strip()

        # Command icrasından əvvəl IP ünvanını tapırıq
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', command)
        found_ip = ip_match.group(1) if ip_match else None

        # Əgər əmrdə IP varsa, onu dərhal kontekst yaddaşına yazırıq
        if found_ip:
            self.last_target_ip = found_ip

        # 1. Hücum xülasəsi və statistikalar
        if any(w in cmd for w in ["hücum", "hucum", "stat", "log", "siyahı", "siyahi"]) or cmd == "h":
            threats = self.db.get_all_threats()
            if not threats:
                return "[🤖 AI Agent]: Hələ ki heç bir hücum qeydə alınmayıb."
            
            res = f"[🤖 AI Agent]: Ümumi {len(threats)} təhdid qeydə alınıb:\n"
            res += "-" * 50 + "\n"
            for t in threats[-5:]:
                res += f"📌 ID: {t[0]} | IP: {t[1]} | Növ: {t[2]} | VT: {t[4]} | Bloklanıb: {'Bəli' if t[5] else 'Xeyr'}\n"
            return res

        # 2. IP Blokdan çıxarma əmri (Bütün hərf variantları)
        unblock_keywords = ["unblock", "çıxart", "cixart", "çixart", "sil", "qaldır", "qaldir", "cixard", "çıxard"]
        if any(w in cmd for w in unblock_keywords):
            target_ip = found_ip or self.last_target_ip
            
            if not target_ip:
                # Əgər yaddaşda da IP yoxdursa, bazadan son bloklanan IP-ni götürürük
                threats = self.db.get_all_threats()
                if threats:
                    target_ip = threats[-1][1] # Son təhdid IP-si

            if target_ip:
                success = self.blocker.unblock_ip(target_ip)
                if success:
                    res_ip = target_ip
                    self.last_target_ip = None
                    return f"[🤖 AI Agent]: {res_ip} ünvanı uğurla blokdan çıxarıldı!"
                else:
                    return f"[🤖 AI Agent]: {target_ip} ünvanını blokdan çıxararkən xəta baş verdi."
            else:
                return "[🤖 AI Agent]: Blokdan çıxarmaq üçün aktiv IP tapılmadı. IP ünvanını qeyd edin."

        # 3. Manuel IP Bloklama əmri
        if any(w in cmd for w in ["blokla", "block", "ban"]):
            target_ip = found_ip or self.last_target_ip
            if target_ip:
                self.blocker.block_ip(target_ip)
                return f"[🤖 AI Agent]: {target_ip} ünvanı manuəl olaraq bloklandı."
            else:
                return "[🤖 AI Agent]: Lütfən bloklamaq istədiyiniz IP ünvanını qeyd edin."

        # 4. İstifadəçi TƏKCƏ BİR IP yazdıqda (Məsələn: "192.168.1.100")
        if found_ip and len(cmd.split()) == 1:
            if found_ip in self.blocker.blocked_ips:
                return f"[🤖 AI Agent]: {found_ip} bloklanıb. Blokdan çıxarmaq üçün sadəcə 'çıxart' yazın."
            else:
                return f"[🤖 AI Agent]: {found_ip} üçün nə etmək istəyirsiniz?\n - Bloklamaq üçün: 'blokla'\n - Blokdan çıxarmaq üçün: 'çıxart'"

        return "[🤖 AI Agent]: Anlamadım.\nİstifadə qaydası:\n • 'hücumlar'\n • 'çıxart' (son IP-ni blokdan çıxarır)\n • '192.168.1.100 blokla'\n • '192.168.1.100 çıxart'"
