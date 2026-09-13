import os
import json
from skills.script_writer import ScriptWriter
from skills.scanner import CodeScanner
from skills.deep_code_analyzer import DeepCodeAnalyzer
from skills.honeypot import HoneypotManager
from skills.fixer import CodeFixer
from skills.log_analyzer import LogAnalyzer
from skills.dependency_checker import DependencyChecker
from skills.env_auditor import EnvAuditor
from skills.report_generator import ReportGenerator
from skills.knowledge_base import KnowledgeBase
from skills.file_integrity import FileIntegrityMonitor
from core.neural_brain import NeuralBrain

class AIAgent:
    def __init__(self, db=None, blocker=None):
        self.db = db
        self.blocker = blocker
        self.writer = ScriptWriter()
        self.scanner = CodeScanner()
        self.deep_analyzer = DeepCodeAnalyzer()
        self.honeypot = HoneypotManager(port=8888)
        self.fixer = CodeFixer()
        self.log_analyzer = LogAnalyzer()
        self.dep_checker = DependencyChecker()
        self.env_auditor = EnvAuditor()
        self.reporter = ReportGenerator()
        self.kb = KnowledgeBase()
        self.fim = FileIntegrityMonitor()
        self.brain = NeuralBrain()

    def process_command(self, command):
        mind = self.brain.evaluate(command)
        thought_output = mind["thought_chain"] + "\n" + "-"*50
        
        intent = mind["intent"]
        cmd = command.lower().strip()

        # 1. Honeypot (Tələ Modulu)
        if intent == "HONEYPOT":
            if "başlat" in cmd or "start" in cmd or "aç" in cmd:
                return f"{thought_output}\n" + self.honeypot.start()
            return f"{thought_output}\n" + self.honeypot.check_traps()

        # 2. Dərin Kod Analizi (AST - Gemini-siz)
        if intent == "DEEP_SCAN":
            parts = command.split()
            target_file = parts[-1] if len(parts) > 1 and os.path.exists(parts[-1]) else "core/ai_agent.py"
            issues = self.deep_analyzer.analyze_file(target_file)
            if not issues:
                return f"{thought_output}\n🔬 [AST Dərin Analiz]: `{target_file}` faylında kritik zəiflik tapılmadı."
            return f"{thought_output}\n🔬 [AST Dərin Analiz - `{target_file}`]:\n" + "\n".join(issues)

        # 3. FIM (Fayl Bütövlüyü)
        if intent == "FIM":
            if "baseline" in cmd or "baza" in cmd:
                return f"{thought_output}\n" + self.fim.create_baseline(".")
            return f"{thought_output}\n" + self.fim.check_integrity(".")

        # 4. Öyrənmə / KnowledgeBase
        if intent == "LEARN" or any(cmd.startswith(w) for w in ["oyren", "öyrən"]):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                res = self.kb.ingest_file(parts[1].strip())
                return f"{thought_output}\n{res}"
            return f"{thought_output}\n⚠️ İstifadə qaydası: `öyrən <fayl_yolu>`"

        # 5. SAST Skan
        if intent == "SCAN":
            target_path = "."
            parts = [p for p in command.split() if os.path.exists(p)]
            if parts:
                target_path = parts[0]
            findings, files, errors = self.scanner.run_scan(target_path)
            report_file = self.scanner.save_json_report(findings, files)
            return f"{thought_output}\n🛡️ Skan tamamlandı! {len(findings)} zəiflik tapıldı. Hesabat: `{report_file}`"

        # 6. Düzəliş (Fixer)
        if intent == "FIX":
            if os.path.exists("scan_report.json"):
                with open("scan_report.json", "r", encoding="utf-8") as rf:
                    report_data = json.load(rf)
                return f"{thought_output}\n" + self.fixer.apply_fixes(report_data)
            return f"{thought_output}\n⚠️ `scan_report.json` tapılmadı."

        # 7. Log Analizi
        if intent == "LOG":
            parts = command.split()
            log_file = parts[-1] if len(parts) > 1 and os.path.exists(parts[-1]) else "logs/access.log"
            return f"{thought_output}\n" + self.log_analyzer.analyze_log_file(log_file)

        # 8. Hesabat
        if intent == "REPORT":
            return f"{thought_output}\n" + self.reporter.generate_html_report()

        # 9. Yaddaş Axtarışı
        kb_match = self.kb.search_knowledge(command)
        if kb_match:
            return f"{thought_output}\n🔍 [Öyrənilmiş Yaddaşdan Alınan Cavab]:\n{kb_match}"

        return f"{thought_output}\n🤖 [SI-GUARD Agent]: Əmr tam anlaşılamadı."
