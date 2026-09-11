import re

class PayloadAnalyzer:
    def __init__(self):
        # SQLi və XSS üçün nümunə regex şablonları
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

    def analyze_payload(self, payload):
        """HTTP parametri və ya sorğuda hücum izi axtarır."""
        threats = []

        # SQL Injection yoxlanışı
        for pattern in self.sqli_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append("SQL Injection (SQLi)")
                break

        # XSS yoxlanışı
        for pattern in self.xss_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append("Cross-Site Scripting (XSS)")
                break

        if threats:
            return {"status": "threat_detected", "threats": threats}
        return {"status": "clean"}
