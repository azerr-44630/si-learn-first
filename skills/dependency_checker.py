import os
import json

class DependencyChecker:
    def __init__(self):
        self.vulnerable_packages = {
            "express": "<4.16.0",
            "lodash": "<4.17.21",
            "axios": "<0.21.1",
            "jsonwebtoken": "<8.5.1"
        }

    def check_package_json(self, project_path):
        pkg_path = os.path.join(project_path, "package.json")
        if not os.path.exists(pkg_path):
            return "⚠️ `package.json` faylı tapılmadı."

        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            found_issues = []

            for pkg, ver in deps.items():
                if pkg in self.vulnerable_packages:
                    found_issues.append((pkg, ver, self.vulnerable_packages[pkg]))

            if not found_issues:
                return "🟢 Bütün asılılıqlar (dependencies) təhlükəsiz görünür."

            res = f"⚠️ {len(found_issues)} potensial zəif asılılıq tapıldı:\n"
            for pkg, ver, rec in found_issues:
                res += f" 📦 {pkg} (Cari: {ver}) -> Təhlükəsiz versiya tələbi: {rec}\n"
            return res
        except Exception as e:
            return f"❌ package.json oxunarkən xəta: {str(e)}"
