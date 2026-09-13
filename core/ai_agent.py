import os
import json
from skills.script_writer import ScriptWriter
from skills.scanner import CodeScanner
from skills.fixer import CodeFixer
from skills.log_analyzer import LogAnalyzer
from skills.dependency_checker import DependencyChecker
from skills.env_auditor import EnvAuditor
from skills.report_generator import ReportGenerator
from skills.knowledge_base import KnowledgeBase
from core.neural_brain import NeuralBrain

class AIAgent:
    def __init__(self, db=None, blocker=None):
        self.db = db
        self.blocker = blocker
        self.writer = ScriptWriter()
        self.scanner = CodeScanner()
        self.fixer = CodeFixer()
        self.log_analyzer = LogAnalyzer()
        self.dep_checker = DependencyChecker()
        self.env_auditor = EnvAuditor()
        self.reporter = ReportGenerator()
        self.kb = KnowledgeBase()
        self.brain = NeuralBrain()

    def process_command(self, command):
        # 1. Neyron düşünmə analizi
        mind = self.brain.evaluate(command)
        thought_output = mind["thought_chain"] + "\n" + "-"*50
        
        intent = mind["intent"]
        cmd = command.lower().strip()

        # 2. Öyrənmə / Ingestion
        if intent == "LEARN" or any(cmd.startswith(w) for w in ["oyren", "öyrən"]):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                res = self.kb.ingest_file(parts[1].strip())
                return f"{thought_output}\n{res}"
            return f"{thought_output}\n⚠️ İstifadə qaydası: `öyrən <fayl_yolu>`"

        # 3. SAST Skan
        if intent == "SCAN":
            target_path = "."
            parts = [p for p in command.split() if os.path.exists(p)]
            if parts:
                target_path = parts[0]
            findings, files, errors = self.scanner.run_scan(target_path)
            report_file = self.scanner.save_json_report(findings, files)
            return f"{thought_output}\n🛡️ Skan tamamlandı! {len(findings)} zəiflik tapıldı. Hesabat: `{report_file}`"

        # 4. Düzəliş
        if intent == "FIX":
            if os.path.exists("scan_report.json"):
                with open("scan_report.json", "r", encoding="utf-8") as rf:
                    report_data = json.load(rf)
                return f"{thought_output}\n" + self.fixer.apply_fixes(report_data)
            return f"{thought_output}\n⚠️ `scan_report.json` tapılmadı."

        # 5. Log Analizi
        if intent == "LOG":
            parts = command.split()
            log_file = parts[-1] if len(parts) > 1 and os.path.exists(parts[-1]) else "logs/access.log"
            return f"{thought_output}\n" + self.log_analyzer.analyze_log_file(log_file)

        # 6. Hesabat
        if intent == "REPORT":
            return f"{thought_output}\n" + self.reporter.generate_html_report()

        # 7. Bilik Bazası Axtarışı
        kb_match = self.kb.search_knowledge(command)
        if kb_match:
            return f"{thought_output}\n🔍 [Öyrənilmiş Yaddaşdan Alınan Cavab]:\n{kb_match}"

        return f"{thought_output}\n🤖 [SI-GUARD Agent]: Əmr tam anlaşılamadı. Mövcud biliklər siyahısı üçün 'biliklər' yazın."
