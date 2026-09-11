import os
import threading
import time
from dotenv import load_dotenv
from core.ui import TerminalUI
from core.analyzer import PayloadAnalyzer
from core.log_monitor import LogMonitor
from skills.threat_intel import ThreatIntel

load_dotenv()

def simulate_attacks(log_file):
    """Sistemi test etmək üçün log faylına avtomatik zərərli sorğular yazır."""
    time.sleep(2)
    sample_logs = [
        '192.168.1.50 - - [11/Sep/2026:17:45:10] "GET /index.php HTTP/1.1" 200 1024',
        '45.33.32.156 - - [11/Sep/2026:17:45:12] "GET /login?user=admin\'%20OR%201=1-- HTTP/1.1" 401 512',
        '185.220.101.5 - - [11/Sep/2026:17:45:15] "GET /search?q=<script>alert(1)</script> HTTP/1.1" 200 2048'
    ]
    with open(log_file, 'a') as f:
        for log in sample_logs:
            f.write(log + '\n')
            f.flush()
            time.sleep(3)

def main():
    ui = TerminalUI()
    ui.print_header()

    intel = ThreatIntel()
    analyzer = PayloadAnalyzer()
    log_path = "logs/access.log"

    monitor = LogMonitor(log_path, analyzer, intel)

    # Test simulyasiyasını arxa fonda işə salırıq
    threading.Thread(target=simulate_attacks, args=(log_path,), daemon=True).start()

    # Canlı izləməni başladırıq
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
