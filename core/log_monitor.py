import time
import os
import re

class LogMonitor:
    def __init__(self, log_file_path, analyzer, threat_intel, db, blocker):
        self.log_file_path = log_file_path
        self.analyzer = analyzer
        self.intel = threat_intel
        self.db = db
        self.blocker = blocker

    def start_monitoring(self):
        if not os.path.exists(self.log_file_path):
            print(f"[!] Log faylı tapılmadı: {self.log_file_path}")
            return

        print(f"[*] Real-vaxt log izləmə başladı: {self.log_file_path}")
        
        with open(self.log_file_path, 'r') as file:
            file.seek(0, os.SEEK_END)
            while True:
                line = file.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                self._process_log_line(line)

    def _process_log_line(self, line):
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
        if ip_match:
            ip = ip_match.group(1)
            analysis = self.analyzer.analyze_payload(line, ip=ip)
            
            if analysis["status"] == "threat_detected":
                threat_type = ', '.join(analysis['threats'])
                print(f"\n[XƏBƏRDARLIQ] Hücum Aşkar Edildi!")
                print(f" -> Mənbə IP: {ip}")
                print(f" -> Təhdid Növü: {threat_type}")
                
                vt_res = self.intel.check_ip(ip)
                vt_malicious = vt_res.get('malicious', 0) if vt_res.get("status") == "success" else 0
                
                is_blocked = self.blocker.block_ip(ip)
                
                self.db.log_threat(
                    ip=ip,
                    threat_type=threat_type,
                    raw_log=line.strip(),
                    vt_malicious=vt_malicious,
                    blocked=1 if is_blocked else 0
                )
                print(f" -> [DB] Təhdid məlumatı SQLite bazasına yazıldı.")
