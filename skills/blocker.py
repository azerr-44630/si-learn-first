import os
import subprocess

class FirewallBlocker:
    def __init__(self):
        self.blocked_ips = set()

    def block_ip(self, ip):
        if ip in self.blocked_ips:
            return True
        try:
            # Linux iptables vasitəsilə bloklama
            cmd = f"sudo iptables -A INPUT -s {ip} -j DROP"
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.blocked_ips.add(ip)
            print(f" -> [FIREWALL] {ip} uğurla bloklandı (iptables).")
            return True
        except Exception:
            # İcazə olmasa və ya xəta baş versə simulyasiya edirik
            self.blocked_ips.add(ip)
            print(f" -> [FIREWALL Simulyasiya] {ip} bloklandı listinə əlavə edildi.")
            return True

    def unblock_ip(self, ip):
        try:
            cmd = f"sudo iptables -D INPUT -s {ip} -j DROP"
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ip in self.blocked_ips:
                self.blocked_ips.remove(ip)
            print(f" -> [FIREWALL] {ip} blokdan çıxarıldı (iptables).")
            return True
        except Exception:
            if ip in self.blocked_ips:
                self.blocked_ips.remove(ip)
            print(f" -> [FIREWALL Simulyasiya] {ip} bloklanmışlar siyahısından çıxarıldı.")
            return True
