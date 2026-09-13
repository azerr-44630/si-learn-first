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
        target = mind.get("target", ".")
        cmd = command.lower().strip()

        # Makro-Plan İcrası (Çoxlu-addımlı avtonom reaksiya)
        if intent == "MACRO_PLAN":
            results = [thought_output]
            for step in mind["plan_steps"]:
                if step == "FIM":
                    results.append("🔍 [Addım 1]: " + self.fim.check_integrity(target))
                elif step == "FIM_BASELINE":
                    results.append("📸 [Addım 1]: " + self.fim.create_baseline(target))
                elif step == "SCAN":
                    findings, files, _ = self.scanner.run_scan(target)
                    results.append(f"🛡️ [Addım 2]: SAST Skan tamamlandı ({len(findings)} zəiflik tapıldı).")
                elif step == "DEEP_SCAN":
                    issues = self.deep_analyzer.analyze_file("core/ai_agent.py")
                    results.append(f"🔬 [Addım 3]: AST Dərin Skan tamamlandı ({len(issues)} xəbərdarlıq).")
                elif step == "LOG":
                    log_res = self.log_analyzer.analyze_log_file("logs/access.log")
                    results.append("📊 [Addım 4]: Log Analizi tamamlandı.")
                elif step == "HONEYPOT_START":
                    results.append("🍯 [Addım 2]: " + self.honeypot.start())
            return "\n\n".join(results)

        # 1. Honeypot (Tələ Modulu)
        if intent == "HONEYPOT":
            if "başlat" in cmd or "start" in cmd or "aç" in cmd:
                return f"{thought_output}\n" + self.honeypot.start()
            return f"{thought_output}\n" + self.honeypot.check_traps()

        # 2. Dərin Kod Analizi (AST)
        if intent == "DEEP_SCAN":
            issues = self.deep_analyzer.analyze_file(target if target != "." else "core/ai_agent.py")
            if not issues:
                return f"{thought_output}\n🔬 [AST Dərin Analiz]: `{target}` faylında kritik zəiflik tapılmadı."
            return f"{thought_output}\n🔬 [AST Dərin Analiz - `{target}`]:\n" + "\n".join(issues)

        # 3. FIM (Fayl Bütövlüyü)
        if intent == "FIM":
            if "baseline" in cmd or "baza" in cmd:
                return f"{thought_output}\n" + self.fim.create_baseline(target)
            return f"{thought_output}\n" + self.fim.check_integrity(target)

        # 4. Öyrənmə / KnowledgeBase
        if intent == "LEARN" or any(cmd.startswith(w) for w in ["oyren", "öyrən"]):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                res = self.kb.ingest_file(parts[1].strip())
                return f"{thought_output}\n{res}"
            return f"{thought_output}\n⚠️ İstifadə qaydası: `öyrən <fayl_yolu>`"

        # 5. SAST Skan
        if intent == "SCAN":
            findings, files, errors = self.scanner.run_scan(target)
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
            return f"{thought_output}\n" + self.log_analyzer.analyze_log_file("logs/access.log")

        # 8. Hesabat
        if intent == "REPORT":
            return f"{thought_output}\n" + self.reporter.generate_html_report()

        # 9. Yaddaş Axtarışı
        kb_match = self.kb.search_knowledge(command)
        if kb_match:
            return f"{thought_output}\n🔍 [Öyrənilmiş Yaddaşdan Alınan Cavab]:\n{kb_match}"

        return f"{thought_output}\n🤖 [SI-GUARD Agent]: Əmr tam anlaşılamadı."
