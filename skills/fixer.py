import os
import re

class CodeFixer:
    def __init__(self):
        pass

    def apply_fixes(self, report_data):
        findings = report_data.get("findings", [])
        if not findings:
            return "⚠️ Düzəldilməli heç bir zəiflik tapılmadı."

        modified_files = set()
        fixed_count = 0

        # Fayllara görə zəiflikləri qruplaşdırırıq
        files_map = {}
        for f in findings:
            filepath = f.get("file")
            if filepath not in files_map:
                files_map[filepath] = []
            files_map[filepath].append(f)

        for filepath, file_findings in files_map.items():
            if not os.path.exists(filepath):
                continue

            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            new_content = content

            for rule in file_findings:
                rule_id = rule.get("rule_id")

                # AUTH-001: Role parametri birbaşa req-dən oxunursa
                if rule_id == "AUTH-001":
                    new_content = re.sub(
                        r'req\.(body|cookies|query)\.role',
                        'req.user?.role',
                        new_content
                    )
                    fixed_count += 1

                # COOKIE-001: Cookie təhlükəsizlik bayraqları əlavə edilir
                elif rule_id == "COOKIE-001":
                    pattern = r'res\.cookie\(\s*(["\'][^"\']+["\'])\s*,\s*([^,)]+)\s*\)'
                    replacement = r"res.cookie(\1, \2, { httpOnly: true, secure: true, sameSite: 'strict' })"
                    new_content = re.sub(pattern, replacement, new_content)
                    fixed_count += 1

                # XSS-001: innerHTML -> textContent əvəzlənməsi
                elif rule_id == "XSS-001":
                    new_content = re.sub(
                        r'(\b\w+)\.innerHTML\s*=\s*([^;]+)',
                        r'\1.textContent = \2',
                        new_content
                    )
                    fixed_count += 1

                # CORS-001: Wildcard CORS düzəlişi
                elif rule_id == "CORS-001":
                    new_content = re.sub(
                        r'origin\s*:\s*["\']\*["\']',
                        "origin: process.env.ALLOWED_ORIGIN || 'http://localhost:3000'",
                        new_content
                    )
                    fixed_count += 1

            if new_content != content:
                # Orijinal faylın ehtiyat nüsxəsini yaradırıq
                backup_path = f"{filepath}.bak"
                with open(backup_path, "w", encoding="utf-8") as bf:
                    bf.write(content)

                # Düzəldilmiş məzmunu yazırıq
                with open(filepath, "w", encoding="utf-8") as wf:
                    wf.write(new_content)

                modified_files.add(filepath)

        return (
            f"🛠️ [🤖 SI-GUARD Fixer]: Yekun nəticə:\n"
            f"✅ Uğurla yamandı: {fixed_count} zəiflik\n"
            f"📁 Yenilənən fayllar: {len(modified_files)} ədəd\n"
            f"💡 Qeyd: Düzəlişdən əvvəlki orijinal fayllar `.bak` genişlənməsi ilə yadda saxlanıldı."
        )
