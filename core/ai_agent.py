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

    def process_command(self, command):
        cmd = command.lower().strip()

        # 1. Öyrənmə / Anlama Modu (Faylı oxuyub yaddaşa yazmaq)
        if any(cmd.startswith(w) for w in ["oyren", "öyrən", "oxu", "ingest"]):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                return self.kb.ingest_file(parts[1].strip())
            return "⚠️ İstifadə qaydası: `öyrən <fayl_yolu>` (Nümunə: `öyrən ders.txt` və ya `öyrən docs.pdf`)"

        # 2. Öyrənilmiş mənbələrin siyahısını göstərmək
        if any(w in cmd for w in ["bilikler", "biliklər", "menbeler", "mənbələr", "sources"]):
            return self.kb.list_sources()

        # 3. Log Analizi
        if "log" in cmd:
            parts = command.split()
            log_file = parts[-1] if len(parts) > 1 and os.path.exists(parts[-1]) else "access.log"
            return self.log_analyzer.analyze_log_file(log_file)

        # 4. Dependency Yoxlanışı
        if any(w in cmd for w in ["dependency", "paket", "package", "npm"]):
            return self.dep_checker.check_package_json(".")

        # 5. Env Auditi
        if "env" in cmd:
            return self.env_auditor.audit(".")

        # 6. HTML Hesabat
        if any(w in cmd for w in ["hesabat", "report", "html"]):
            return self.reporter.generate_html_report()

        # 7. Skaner (SAST)
        if any(w in cmd for w in ["skan", "scan", "zeiflik", "zəiflik"]):
            target_path = "."
            parts = [p for p in command.split() if os.path.exists(p)]
            if parts:
                target_path = parts[0]
            findings, files, errors = self.scanner.run_scan(target_path)
            report_file = self.scanner.save_json_report(findings, files)
            return f"🛡️ Skan tamamlandı! {len(findings)} zəiflik aşkar edildi. Hesabat: `{report_file}`"

        # 8. Düzəliş (Fixer)
        if any(w in cmd for w in ["düzəlt", "duzelt", "fix"]):
            if os.path.exists("scan_report.json"):
                with open("scan_report.json", "r", encoding="utf-8") as rf:
                    report_data = json.load(rf)
                return self.fixer.apply_fixes(report_data)
            return "⚠️ `scan_report.json` tapılmadı."

        # 9. Bilik Bazası Axtarışı (Sual verildikdə öyrənilənlərdən cavab tapmaq)
        kb_match = self.kb.search_knowledge(command)
        if kb_match:
            return f"🔍 Agent daxili yaddaşından tapılan məlumat:\n{kb_match}"

        return "🤖 [SI-GUARD Agent]: Əmr anlaşılamadı.\nYeni Əmrlər: 'öyrən <fayl>', 'biliklər'."
