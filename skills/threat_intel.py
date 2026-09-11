import os
import requests

class ThreatIntel:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("VIRUSTOTAL_API_KEY")
        self.base_url = "https://www.virustotal.com/api/v3"

    def check_ip(self, ip_address):
        """IP ünvanının reputasiyasını VirusTotal vasitəsilə yoxlayır."""
        if not self.api_key:
            return {"status": "error", "message": "API key təyin edilməyib!"}

        headers = {
            "accept": "application/json",
            "x-apikey": self.api_key
        }
        url = f"{self.base_url}/ip_addresses/{ip_address}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                return {
                    "status": "success",
                    "ip": ip_address,
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless": stats.get("harmless", 0)
                }
            return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
