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

    # Log izləməni arxa fonda (background thread) başladırıq
    monitor_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
    monitor_thread.start()

    print("\n[🤖] AI Agent Çat Rejimi Aktivdir! (Çıxış üçün 'exit' yazın)")
    print("-" * 55)

    # İnteraktiv AI Çat Dövrəsi
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
