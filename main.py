import os
from dotenv import load_dotenv
from core.ui import TerminalUI
from core.analyzer import PayloadAnalyzer
from skills.threat_intel import ThreatIntel

load_dotenv()

def main():
    ui = TerminalUI()
    ui.print_header()

    intel = ThreatIntel()
    analyzer = PayloadAnalyzer()

    # 1. IP Reputasiya Testi
    target_ip = "8.8.8.8"
    print(f"\n[1] IP Analizi: {target_ip}")
    res = intel.check_ip(target_ip)
    if res.get("status") == "success":
        print(f"    [+] Zərərli: {res['malicious']} | Təhlükəsiz: {res['harmless']}")

    # 2. Payload Analiz Testi (Test üçün zərərli sorğular)
    test_payloads = [
        "admin' OR 1=1 --",
        "<script>alert('XSS')</script>",
        "user_id=125&name=almas"
    ]

    print("\n[2] Sorğu (Payload) Analizi Testləri:")
    for p in test_payloads:
        result = analyzer.analyze_payload(p)
        if result["status"] == "threat_detected":
            print(f"    [!] TƏHDİD TAPILDI -> '{p}' | Tür: {', '.join(result['threats'])}")
        else:
            print(f"    [✓] Təmiz -> '{p}'")

if __name__ == "__main__":
    main()
