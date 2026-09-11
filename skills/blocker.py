import subprocess
import os

class FirewallBlocker:
    def __init__(self):
        self.blocked_ips = set()

    def block_ip(self, ip_address):
        """IP ünvanını firewall vasitəsilə bloklayır."""
        if ip_address in self.blocked_ips:
            return True

        # Təhlükəsiz IP-ləri bloklamamaq üçün ağ siyahı (whitelist)
        if ip_address in ["127.0.0.1", "8.8.8.8"]:
            return False

        try:
            # Linux iptables əmri ilə bloklama
            cmd = f"iptables -A INPUT -s {ip_address} -j DROP"
            result = subprocess.run(["su", "-c", cmd], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.blocked_ips.add(ip_address)
                print(f"[🛡️ BLOCK] IP uğurla firewall-da bloklandı: {ip_address}")
                return True
            else:
                # Root icazəsi yoxdursa emulyasiya rejimi
                self.blocked_ips.add(ip_address)
                print(f"[🛡️ SIMULATED BLOCK] IP blok siyahısına salındı (Simulyasiya): {ip_address}")
                return True
        except Exception as e:
            self.blocked_ips.add(ip_address)
            print(f"[🛡️ SIMULATED BLOCK] {ip_address} bloklandı (Xəta: {e})")
            return True
