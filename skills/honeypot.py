import http.server
import socketserver
import threading
import datetime
import os

class HoneypotHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self._log_and_respond()

    def do_POST(self):
        self._log_and_respond()

    def _log_and_respond(self):
        client_ip = self.client_address[0]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] 🍯 [HONEYPOT TƏLƏSİ] IP: {client_ip} | Yol: {self.path} | Metod: {self.command}\n"
        
        os.makedirs("logs", exist_ok=True)
        with open("logs/honeypot.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>404 Not Found</h1></body></html>")

class HoneypotManager:
    _server_instance = None
    _thread_instance = None

    def __init__(self, port=8888):
        self.port = port

    def start(self):
        if HoneypotManager._server_instance:
            return f"⚠️ Honeypot artıq port {self.port} üzərində fonda aktivdir!"
        try:
            handler = HoneypotHandler
            HoneypotManager._server_instance = socketserver.TCPServer(("", self.port), handler)
            HoneypotManager._thread_instance = threading.Thread(target=HoneypotManager._server_instance.serve_forever, daemon=True)
            HoneypotManager._thread_instance.start()
            return f"🍯 [HONEYPOT AKTİVLƏŞDİ]: Saxta port {self.port} üzərindən tələ işə salındı. Hücum kütləsi `logs/honeypot.log` faylına tutulur."
        except Exception as e:
            return f"❌ Honeypot başladılarkən xəta: {str(e)}"

    def check_traps(self):
        if not os.path.exists("logs/honeypot.log"):
            return "🍯 Hələ heç bir tələyə düşən hücumçu qeydə alınmayıb."
        with open("logs/honeypot.log", "r", encoding="utf-8") as f:
            logs = f.readlines()
        return f"🍯 [TƏLƏ LOGLARI - Son {len(logs)} Hücum Cəhdi]:\n" + "".join(logs[-5:])
