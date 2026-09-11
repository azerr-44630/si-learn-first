import os
import re
import sys
import json
import subprocess
import shutil
from datetime import datetime, timezone

SEVERITY_ORDER = {"KRITIK": 0, "YUKSEK": 1, "ORTA": 2, "ASAGI": 3, "MELUMAT": 4}

class Finding:
    def __init__(self, rule_id, title, severity, file, line, snippet, explanation, recommendation):
        self.rule_id = rule_id
        self.title = title
        self.severity = severity
        self.file = file
        self.line = line
        self.snippet = snippet.strip()[:160]
        self.explanation = explanation
        self.recommendation = recommendation

    def to_dict(self):
        return self.__dict__

class Rule:
    def __init__(self, rule_id, title, severity, pattern, explanation, recommendation,
                 file_types=(".js",), flags=re.IGNORECASE, negative_context=None):
        self.rule_id = rule_id
        self.title = title
        self.severity = severity
        self.pattern = re.compile(pattern, flags)
        self.explanation = explanation
        self.recommendation = recommendation
        self.file_types = file_types
        self.negative_context = re.compile(negative_context, flags) if negative_context else None

    def applies_to(self, filepath):
        return filepath.lower().endswith(self.file_types)

    def scan(self, filepath, content):
        findings = []
        if self.negative_context and self.negative_context.search(content):
            return findings
        for m in self.pattern.finditer(content):
            line_no = content.count("\n", 0, m.start()) + 1
            line_text = content.splitlines()[line_no - 1] if line_no - 1 < len(content.splitlines()) else m.group(0)
            findings.append(Finding(
                self.rule_id, self.title, self.severity, filepath, line_no,
                line_text, self.explanation, self.recommendation
            ))
        return findings

RULES = [
    Rule(
        rule_id="AUTH-001",
        title="Rol/icaze melumati client-den birbasa qebul edilir (Privilege Escalation)",
        severity="KRITIK",
        pattern=r"(req\.body\.role|req\.cookies\.role|req\.query\.role)",
        explanation="Istifadecinin 'role' statusu client terefinden gonderilen melumatdan birbasa oxunur.",
        recommendation="Rolu YALNIZ server terefinde, autentifikasiya olunmus sessiya/JWT payload-undan oxu."
    ),
    Rule(
        rule_id="AUTH-002",
        title="Qorunmali route-da autentifikasiya middleware-i gorunmur",
        severity="YUKSEK",
        pattern=r"app\.(get|post|put|delete)\(\s*['\"](?:/api/admin|/api/user|/api/profile|/api/ticket)[^'\"]*['\"]\s*,\s*(?:async\s*)?\(",
        explanation="Hessas path-dir, amma sorgu handler-dan evvel auth middleware cagirilmayib.",
        recommendation="Hessas her route-un ikinci parametri bir auth middleware olmalidir."
    ),
    Rule(
        rule_id="COOKIE-001",
        title="Cookie 'httpOnly' ve ya 'signed' bayragi olmadan qoyulur",
        severity="YUKSEK",
        pattern=r"res\.cookie\(\s*['\"][^'\"]+['\"]\s*,\s*[^,)]+\s*\)",
        explanation="res.cookie() cagirisinda options obyekti yoxdur. Cookie XSS-e ve ya forgeable olmaga aciqdir.",
        recommendation="res.cookie('ban', value, { httpOnly: true, signed: true, secure: true, sameSite: 'strict' }) istifade et."
    ),
    Rule(
        rule_id="XSS-001",
        title="innerHTML server/client-den gelen deyerle doldurulur (XSS riski)",
        severity="YUKSEK",
        pattern=r"\.innerHTML\s*=\s*(?!['\"`]\s*['\"`])[^;]+",
        explanation="innerHTML-e birbasa deyisken elave edilir, Stored/Reflected XSS riski yaradir.",
        recommendation="innerHTML yerine .textContent istifade et ve ya DOMPurify ile sanitize et.",
        file_types=(".js", ".html")
    ),
    Rule(
        rule_id="SQLI-001",
        title="SQL sorgusu string concatenation/template ile qurulur",
        severity="KRITIK",
        pattern=r"(query|execute)\(\s*(`[^`]*\$\{|['\"][^'\"]*['\"]\s*\+|[^,)]+\+\s*req\.)",
        explanation="SQL sorgusu string birlesdirmesi ile qurulub. SQL Injection acigidir.",
        recommendation="Her zaman parametrized query istifade et: pool.query('SELECT * FROM users WHERE email=$1', [email])"
    ),
    Rule(
        rule_id="OTP-001",
        title="OTP/login route-unda rate-limit middleware-i tapilmadi",
        severity="ORTA",
        pattern=r"app\.post\(\s*['\"][^'\"]*(otp|login|verify)[^'\"]*['\"]",
        explanation="OTP/login endpoint-i rate-limit olmadan gorunur. Brute-force hucumuna aciqdir.",
        recommendation="express-rate-limit paketi elave et ve bu route-a tetbiq et.",
        negative_context=r"rate-?limit|rateLimit\("
    ),
    Rule(
        rule_id="SECRET-001",
        title="Sabit kodlanmis (hardcoded) secret/parol/API acari gorunur",
        severity="KRITIK",
        pattern=r"(?:password|secret|api[_-]?key|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]",
        explanation="Kodun icinde parol/acar birbasa yazilib.",
        recommendation="Butun sirri melumatlari .env faylina kocur ve process.env.ADI ile oxu.",
        file_types=(".js",)
    ),
    Rule(
        rule_id="ADFRAUD-001",
        title="Reklam baxisi (ad-view) puan/bilet artimi client sorgusundan birbasa qebul edilir",
        severity="ORTA",
        pattern=r"app\.post\(\s*['\"][^'\"]*ad[-_]?view[^'\"]*['\"]",
        explanation="Ad-view endpoint-i server-side verification olmadan puan artirir.",
        recommendation="Google Ad Manager H5 Games Ads-in SSV callback-ini istifade et."
    ),
    Rule(
        rule_id="CORS-001",
        title="CORS butun originlere acigdir (wildcard)",
        severity="ORTA",
        pattern=r"(cors\(\s*\{\s*origin\s*:\s*['\"]\*['\"]|Access-Control-Allow-Origin['\"]\s*,\s*['\"]\*['\"])",
        explanation="CORS ayari '*' qebul edir. Credential daxil olan sorgularda tehlukelidir.",
        recommendation="origin: ['https://sizin-domeniniz.com'] kimi konkret siyahi ver."
    ),
    Rule(
        rule_id="EVAL-001",
        title="eval() ve ya Function() ile dinamik kod icra edilir",
        severity="YUKSEK",
        pattern=r"\b(eval|new Function)\s*\(",
        explanation="eval/Function istifadeci melumati ile birlesse RCE acigi yaradir.",
        recommendation="eval/Function-dan tamamen qacin."
    ),
]

class CodeScanner:
    def __init__(self):
        self.temp_dir = "temp_repo"

    def fetch_github_repo(self, repo_url):
        """GitHub linkini klonlayır və ya endirir."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # git clone əmri
        cmd = ["git", "clone", "--depth", "1", repo_url, self.temp_dir]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            return False, res.stderr
        return True, self.temp_dir

    def cleanup_temp(self):
        """Müvəqqəti repo papkasını təmizləyir."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def collect_files(self, target):
        if os.path.isfile(target):
            return [target]
        files = []
        for root, _, filenames in os.walk(target):
            if "node_modules" in root or ".git" in root:
                continue
            for fn in filenames:
                if fn.lower().endswith((".js", ".html")):
                    files.append(os.path.join(root, fn))
        return files

    def run_scan(self, target):
        files = self.collect_files(target)
        all_findings = []
        errors = []

        for fp in files:
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for rule in RULES:
                    if rule.applies_to(fp):
                        all_findings.extend(rule.scan(fp, content))
            except Exception as e:
                errors.append((fp, str(e)))

        all_findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.file, f.line))
        return all_findings, files, errors

    def save_json_report(self, findings, files, out_path="scan_report.json"):
        data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scanned_files": files,
            "total_findings": len(findings),
            "findings": [f.to_dict() for f in findings],
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return out_path
