import os
import re
import json
from skills.script_writer import ScriptWriter
from skills.scanner import CodeScanner
from skills.fixer import CodeFixer

class AIAgent:
    def __init__(self, db, blocker):
        self.db = db
        self.blocker = blocker
        self.writer = ScriptWriter()
        self.scanner = CodeScanner()
        self.fixer = CodeFixer()
        self.last_target_ip = None

    def process_command(self, command):
        cmd = command.lower().strip()

        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', command)
        found_ip = ip_match.group(1) if ip_match else None

        if found_ip:
            self.last_target_ip = found_ip

        # 1. Statik Kod və Təhlükəsizlik Skaneri (SI-GUARD Scanner)
        if any(w in cmd for w in ["skan", "scan", "zeiflik", "zəiflik", "scanner", "github.com"]):
            github_match = re.search(r'https?://github\.com/[^\s]+', command)
            
            is_github = False
            if github_match:
                repo_url = github_match.group(0)
                is_github = True
                print(f"⏳ [🤖 SI-GUARD Scanner]: GitHub-dan kodlar yüklənir ({repo_url})...")
                success, target_path_or_err = self.scanner.fetch_github_repo(repo_url)
                if not success:
                    return f"❌ [🤖 SI-GUARD Scanner]: GitHub-dan yükləmə uğursuz oldu:\n{target_path_or_err}"
                target_path = target_path_or_err
            else:
                ignore_words = ["skan", "scan", "et", "scanner", "scanner.py", "python3", "zeiflik", "zəiflik"]
                parts = [p for p in command.split() if p.lower() not in ignore_words]

                target_path = "."
                if parts:
                    candidate = parts[0]
                    if os.path.exists(candidate):
                        target_path = candidate
                    else:
                        return f"❌ [🤖 SI-GUARD Scanner]: Xəta! `{candidate}` faylı və ya qovluğu tapılmadı."

            findings, files, errors = self.scanner.run_scan(target_path)

            if not files:
                if is_github:
                    self.scanner.cleanup_temp()
                return f"⚠️ [🤖 SI-GUARD Scanner]: `{target_path}` daxilində skan edilə biləcək `.js` və ya `.html` faylı tapılmadı."

            report_file = self.scanner.save_json_report(findings, files)

            if not findings:
                if is_github:
                    self.scanner.cleanup_temp()
                return (
                    f"🛡️ [🤖 SI-GUARD Scanner]: Skan tamamlandı!\n"
                    f"📁 Taranan fayllar ({len(files)}): {', '.join([os.path.basename(f) for f in files])}\n"
                    f"🟢 Heç bir tanınan zəiflik pattern-i tapılmadı."
                )

            res = f"🛡️ [🤖 SI-GUARD Scanner]: {len(findings)} zəiflik aşkar edildi!\n"
            res += f"📁 Taranan fayllar ({len(files)}): {', '.join([os.path.basename(f) for f in files])} | 💾 Hesabat: `{report_file}`\n"
            res += "=" * 50 + "\n"
            
            for f in findings[:5]:
                icon = {"KRITIK": "🔴", "YUKSEK": "🟠", "ORTA": "🟡", "ASAGI": "🔵"}.get(f.severity, "⚪")
                res += f"{icon} [{f.severity}] {f.rule_id} — {f.title}\n"
                res += f"   📍 Fayl: {os.path.basename(f.file)}:{f.line}\n"
                res += f"   💡 Təklif: {f.recommendation}\n\n"

            if len(findings) > 5:
                res += f"⚠️ Və daha {len(findings) - 5} təhdid... Bütün detallar `{report_file}` faylına yazıldı.\n"

            res += "\n💡 Zəiflikləri avtomatik düzəltmək üçün 'düzəlt' əmrini verin."
            return res

        # 2. Avtomatik Zəiflik Düzəltmə (Fixer)
        if any(w in cmd for w in ["düzəlt", "duzelt", "fix", "patch"]):
            report_path = "scan_report.json"
            if not os.path.exists(report_path):
                return "⚠️ [🤖 SI-GUARD Fixer]: Hesabat faylı (`scan_report.json`) tapılmadı. Əvvəlcə 'skan' əmrini icra edin."
            
            try:
                with open(report_path, "r", encoding="utf-8") as rf:
                    report_data = json.load(rf)
                return self.fixer.apply_fixes(report_data)
            except Exception as e:
                return f"❌ [🤖 SI-GUARD Fixer]: Düzəliş zamanı xəta baş verdi: {str(e)}"

        # 3. Skript Və Kod Yazma Əmri
        if any(w in cmd for w in ["skript", "script", "kod", "kod yaz", "skript yaz"]):
            code, filename = self.writer.generate_script(cmd)
            return (
                f"📝 [🤖 SI Script Generator]: Tələbinizə uyğun skript hazırlandı!\n\n"
                f"📄 Fayl adı: `{filename}`\n"
                f"```bash\n{code}```\n"
                f"💡 Bu skripti istifadə etmək üçün terminalda `cat > {filename}` əmri ilə yaddaşa yaza bilərsiniz."
            )

        # 4. Hücum xülasəsi
        if any(w in cmd for w in ["hücum", "hucum", "stat", "log", "siyahı", "siyahi"]) or cmd == "h":
            threats = self.db.get_all_threats()
            if not threats:
                return "[🤖 AI Agent]: Hələ ki heç bir hücum qeydə alınmayıb."
            
            res = f"[🤖 AI Agent]: Ümumi {len(threats)} təhdid qeydə alınmışdır:\n"
            res += "-" * 50 + "\n"
            for t in threats[-5:]:
                res += f"📌 ID: {t[0]} | IP: {t[1]} | Növ: {t[2]} | VT: {t[4]} | Bloklanıb: {'Bəli' if t[5] else 'Xeyr'}\n"
            return res

        # 5. IP Blokdan çıxarma əmri
        unblock_keywords = ["unblock", "çıxart", "cixart", "çixart", "sil", "qaldır", "qaldir", "cixard", "çıxard"]
        if any(w in cmd for w in unblock_keywords):
            target_ip = found_ip or self.last_target_ip
            if not target_ip:
                threats = self.db.get_all_threats()
                if threats:
                    target_ip = threats[-1][1]

            if target_ip:
                success = self.blocker.unblock_ip(target_ip)
                if success:
                    res_ip = target_ip
                    self.last_target_ip = None
                    return f"[🤖 AI Agent]: {res_ip} ünvanı uğurla blokdan çıxarıldı!"
                else:
                    return f"[🤖 AI Agent]: {target_ip} ünvanını blokdan çıxararkən xəta baş verdi."
            else:
                return "[🤖 AI Agent]: Blokdan çıxarmaq üçün aktiv IP tapılmadı."

        # 6. Manuel IP Bloklama əmri
        if any(w in cmd for w in ["blokla", "block", "ban"]):
            target_ip = found_ip or self.last_target_ip
            if target_ip:
                self.blocker.block_ip(target_ip)
                return f"[🤖 AI Agent]: {target_ip} ünvanı manuəl olaraq bloklandı."
            else:
                return "[🤖 AI Agent]: Lütfən bloklamaq istədiyiniz IP ünvanını qeyd edin."

        return (
            "[🤖 AI Agent]: Anlamadım.\n"
            "İstifadə qaydası:\n"
            " • 'skan <path/url>'\n"
            " • 'düzəlt' (son skan nəticəsindəki zəiflikləri yamayır)\n"
            " • 'skript yaz'\n"
            " • 'hücumlar'"
        )
