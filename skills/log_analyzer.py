import re
import os

class LogAnalyzer:
    def __init__(self):
        self.sqli_pattern = re.compile(r"(UNION|SELECT|INSERT|DELETE|DROP|' OR '1'='1)", re.IGNORECASE)
        self.xss_pattern = re.compile(r"(<script>|javascript:|onerror=|onload=)", re.IGNORECASE)
        self.path_traversal = re.compile(r"(\.\./\.\./|/etc/passwd|\.env)", re.IGNORECASE)

    def analyze_log_file(self, log_path):
        if not os.path.exists(log_path):
            return f"❌ Log faylı tapılmadı: {log_path}"

        suspicious_entries = []
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_no, line in enumerate(f, 1):
                if self.sqli_pattern.search(line):
                    suspicious_entries.append((line_no, "SQLi Cəhdi", line.strip()))
                elif self.xss_pattern.search(line):
                    suspicious_entries.append((line_no, "XSS Cəhdi", line.strip()))
                elif self.path_traversal.search(line):
                    suspicious_entries.append((line_no, "Path Traversal Cəhdi", line.strip()))

        if not suspicious_entries:
            return "🟢 Log faylında heç bir şübhəli fəaliyyət aşkar edilmədi."

        report = f"⚠️ {len(suspicious_entries)} şübhəli sorğu aşkar edildi:\n"
        for line_no, threat_type, content in suspicious_entries[:10]:
            report += f" 📍 Sətir {line_no} | [{threat_type}]: {content[:80]}...\n"
        return report
