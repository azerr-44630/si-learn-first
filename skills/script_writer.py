import os

class ScriptWriter:
    def __init__(self):
        pass

    def generate_script(self, request_text):
        req = request_text.lower().strip()

        if "iptables" in req or "firewall" in req or "sifirla" in req or "sıfırla" in req:
            code = (
                "#!/bin/bash\n"
                "# Blue Team Firewall Reset Script\n\n"
                "echo '[*] IPTables qaydaları sıfırlanır...'\n"
                "iptables -F\n"
                "iptables -X\n"
                "iptables -t nat -F\n"
                "iptables -t nat -X\n"
                "iptables -P INPUT ACCEPT\n"
                "iptables -P FORWARD ACCEPT\n"
                "iptables -P OUTPUT ACCEPT\n"
                "echo '[+] Bütün firewall qaydaları silindi və girişlər açıldı!'\n"
            )
            return code, "reset_firewall.sh"

        elif "backup" in req or "baza" in req or "nusxe" in req or "nüsxə" in req:
            code = (
                "import shutil\n"
                "import datetime\n"
                "import os\n\n"
                "def backup_db():\n"
                "    db_file = 'knowledge.db'\n"
                "    if not os.path.exists(db_file):\n"
                "        print('[!] knowledge.db tapılmadı.')\n"
                "        return\n"
                "    date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')\n"
                "    backup_name = f'knowledge_backup_{date_str}.db'\n"
                "    shutil.copy(db_file, backup_name)\n"
                "    print(f'[+] Baza nüsxələndi: {backup_name}')\n\n"
                "if __name__ == '__main__':\n"
                "    backup_db()\n"
            )
            return code, "backup_db.py"

        elif "log" in req or "temizle" in req or "təmizlə" in req:
            code = (
                "#!/bin/bash\n"
                "# Log Təmizləmə Skripti\n"
                "LOG_FILE='logs/access.log'\n"
                "if [ -f \"$LOG_FILE\" ]; then\n"
                "    > \"$LOG_FILE\"\n"
                "    echo '[+] access.log faylı sıfırlandı.'\n"
                "else\n"
                "    echo '[!] Log faylı tapılmadı.'\n"
                "fi\n"
            )
            return code, "clear_logs.sh"

        else:
            code = (
                "#!/bin/bash\n"
                "# Avtonom SI Tərəfindən Yaradılmış Xüsusi Skript\n"
                "echo '[*] Skript icra olunur...'\n"
                "echo '[+] Proses tamamlandı.'\n"
            )
            return code, "custom_script.sh"
