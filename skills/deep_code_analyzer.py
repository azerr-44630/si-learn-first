import ast
import os
import re

class DeepCodeAnalyzer(ast.NodeVisitor):
    """Gemini-siz, 100% yerli AST və Leksil Statik Kod Analizi Modulu"""
    def __init__(self):
        self.issues = []
        self.current_file = ""

    def analyze_file(self, filepath):
        self.current_file = filepath
        self.issues = []
        
        if not os.path.exists(filepath):
            return [f"❌ Fayl tapılmadı: {filepath}"]

        if filepath.endswith('.py'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content, filename=filepath)
                self.visit(tree)
                self._check_hardcoded_secrets(content)
            except SyntaxError as e:
                self.issues.append(f"❌ [SİNTAKSİS XƏTASI]: Sətr {e.lineno} - {e.msg}")
            except Exception as e:
                self.issues.append(f"⚠️ [AST ANALİZ XƏTASI]: {str(e)}")
        else:
            self._regex_fallback_analysis(filepath)

        return self.issues

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec']:
                self.issues.append(f"🚨 [DƏRİN KRİTİK - RCE]: Sətr {node.lineno} -> Dinamik kod icrası (`{node.func.id}`) aşkar edildi!")
        
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['system', 'popen', 'Popen']:
                self.issues.append(f"⚠️ [SİSTEM ƏMRİ]: Sətr {node.lineno} -> Sistem əmri çağırışı (`{node.func.attr}`). Shell Injection ehtimalı.")
            if node.func.attr in ['loads', 'load'] and getattr(node.func.value, 'id', '') == 'pickle':
                self.issues.append(f"🚨 [TƏHLÜKƏLİ DESERİALİZASİYA]: Sətr {node.lineno} -> `pickle.loads` istifadə edilir.")
        
        self.generic_visit(node)

    def _check_hardcoded_secrets(self, content):
        patterns = {
            "Məxfilik Sızıntısı (Secret/Key)": r"(?i)(api_key|secret|password|auth_token)\s*=\s*['\"][A-Za-z0-9_\-]{8,}['\"]",
            "Məxfilik Sızıntısı (Hardcoded IP)": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        }
        for label, pattern in patterns.items():
            matches = re.finditer(pattern, content)
            for m in matches:
                self.issues.append(f"🔐 [{label}]: Hardcoded məlumat tapıldı -> `{m.group(0)[:25]}...`")

    def _regex_fallback_analysis(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            for idx, line in enumerate(lines, 1):
                if "innerHTML" in line:
                    self.issues.append(f"⚠️ Sətr {idx}: DOM XSS riski (`innerHTML`).")
                if ("SELECT" in line or "INSERT" in line) and ("+" in line or "${" in line):
                    self.issues.append(f"🚨 Sətr {idx}: SQL Injection riski (Formatlanmamış sorğu).")
        except Exception as e:
            self.issues.append(f"Fayl oxunma xətası: {e}")
