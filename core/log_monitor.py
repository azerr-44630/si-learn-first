import time
import os
import re

class LogMonitor:
    def __init__(self, log_file_path, analyzer, threat_intel):
        self.log_file_path = log_file_path
        self.analyzer = analyzer
        self.intel = threat_intel

    def start_monitoring(self):
        """Log faylını canlı olaraq (tail -f məntiqli) oxuyur."""
        if not os.path.exists(self.log_file_path):
            print(f"[!] Log faylı tapılmadı: {self.log_file_path}")
            return

        print(f"[*] Real-vaxt log izləmə başladı: {self.log_file_path}")
        
        with open(self.log_file_path, 'r') as file:
            # Faylın sonuna keçirik
            file.seek(0, os.SEEK_END)
            
            while True:
                line = file.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                
                self._process_log_line(line)

    def _process_log_line(self, line):
        """Gələn sətirdən IP və URL/Payload məlumatını ayırır."""
        # Standart Nginx/Apache log formatı üçün IP və Sorğu çıxarma regex-i
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
        if ip_match:
            ip = ip_match.group(1)
            
            # Payload hücum analizi
            analysis = self.analyzer.analyze_payload(line)
            if analysis["status"] == "threat_detected":
                print(f"\n[XƏBƏRDARLIQ] Hücum Aşkar Edildi!")
                print(f" -> Mənbə IP: {ip}")
                print(f" -> Təhdid Növü: {', '.join(analysis['threats'])}")
                print(f" -> Sorğu Sətri: {line.strip()}")
                
                # IP-nin reputasiyasını sorğulayırıq
                vt_res = self.intel.check_ip(ip)
                if vt_res.get("status") == "success":
                    print(f" -> VirusTotal Reputasiyası (Zərərli/Təhlükəsiz): {vt_res['malicious']}/{vt_res['harmless']}")
