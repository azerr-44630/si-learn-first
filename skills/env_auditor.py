import os

class EnvAuditor:
    def __init__(self):
        pass

    def audit(self, project_path):
        issues = []
        env_path = os.path.join(project_path, ".env")
        gitignore_path = os.path.join(project_path, ".gitignore")

        if os.path.exists(env_path):
            issues.append("⚠️ Proyekt qovluğunda `.env` faylı aşkar olundu.")
            
            # .gitignore yoxlanılır
            in_gitignore = False
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    if ".env" in f.read():
                        in_gitignore = True
            
            if not in_gitignore:
                issues.append("🔴 KRİTİK: `.env` faylı `.gitignore` faylına əlavə edilməyib! GitHub-a sızma riski var.")

            # Gizli açarların mövcudluğu
            with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "JWT_SECRET=default" in content or "SECRET=123456" in content:
                    issues.append("🟠 YÜKSƏK: `.env` faylında zəif/standart gizli açarlar istifadə olunur.")
        else:
            issues.append("ℹ️ `.env` faylı tapılmadı.")

        return "\n".join(issues)
