import re
import time

class PayloadAnalyzer:
    def __init__(self):
        self.sqli_patterns = [
            r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
            r"((\%3D)|(=))[^\n]*((%27)|(\')|(\-\-)|(\%3B)|(;))",
            r"\w*\s*(union|select|insert|delete|update|drop|alter)\s*"
        ]
        self.xss_patterns = [
            r"((\%3C)|<)((\%2F)|\/)*[a-z0-9\%]+((\%3E)|>)",
            r"((\%3C)|<)((\%69)|i|(\%49))((%6D)|m|(%4D))((%67)|g|(%47))",
            r"javascript\s*:"
        ]
        # Brute-Force üçün IP-lərin uğursuz cəhd tarixçəsi
        self.failed_attempts = {}

    def analyze_payload(self, payload, ip=None):
        threats = []

        # 1. SQL Injection yoxlanışı
        for pattern in self.sqli_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append("SQL Injection (SQLi)")
                break

        # 2. XSS yoxlanışı
        for pattern in self.xss_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append("Cross-Site Scripting (XSS)")
                break

        # 3. Brute-Force yoxlanışı (HTTP 401 və ya /login sorğuları)
        if ip and (" 401 " in payload or "/login" in payload or "/admin" in payload):
            now = time.time()
            if ip not in self.failed_attempts:
                self.failed_attempts[ip] = []
            
            # Son 10 saniyədən köhnə cəhdləri silirik
            self.failed_attempts[ip] = [t for t in self.failed_attempts[ip] if now - t < 10]
            self.failed_attempts[ip].append(now)

            # Əgər 10 saniyə ərzində 3 və ya daha çox uğursuz cəhd varsa
            if len(self.failed_attempts[ip]) >= 3:
                threats.append("Brute-Force Attack")

        if threats:
            return {"status": "threat_detected", "threats": threats}
        return {"status": "clean"}
