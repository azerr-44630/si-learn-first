import os
import threading
import time
from dotenv import load_dotenv
from core.ui import TerminalUI
from core.analyzer import PayloadAnalyzer
from core.log_monitor import LogMonitor
from core.knowledge_base import KnowledgeBase
from core.ai_agent import AIAgent
from skills.threat_intel import ThreatIntel
from skills.blocker import FirewallBlocker

load_dotenv()

def simulate_attacks(log_file):
    time.sleep(3)
    sample_logs = [
        # Brute-Force Simulyasiyası (Aynı IP-dən ard-arda /login cəhdləri)
        '192.168.1.100 - - [11/Sep/2026:18:00:01] "POST /login HTTP/1.1" 401 256',
        '192.168.1.100 - - [11/Sep/2026:18:00:02] "POST /login HTTP/1.1" 401 256',
        '192.168.1.100 - - [11/Sep/2026:18:00:03] "POST /login HTTP/1.1" 401 256'
    ]
    with open(log_file, 'a') as f:
        for log in sample_logs:
            f.write(log + '\n')
            f.flush()
            time.sleep(1)

def main():
    ui = TerminalUI()
    ui.print_header()

    intel = ThreatIntel()
    analyzer = PayloadAnalyzer()
    db = KnowledgeBase()
    blocker = FirewallBlocker()
    ai = AIAgent(db, blocker)
    
    log_path = "logs/access.log"
    monitor = LogMonitor(log_path, analyzer, intel, db, blocker)

    threading.Thread(target=simulate_attacks, args=(log_path,), daemon=True).start()
    monitor_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
    monitor_thread.start()

    print("\n[🤖] AI Agent Çat Rejimi Aktivdir! (Çıxış üçün 'exit' yazın)")
    print("-" * 55)

    while True:
        try:
            user_cmd = input("\nBlueTeam-AI > ")
            if user_cmd.lower().strip() in ['exit', 'quit']:
                print("[!] Çıxış edilir...")
                break
            if user_cmd.strip():
                response = ai.process_command(user_cmd)
                print(response)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
