import os
import json
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        pass

    def generate_html_report(self, report_json_path="scan_report.json"):
        if not os.path.exists(report_json_path):
            return "❌ Hesabat JSON faylı tapılmadı."

        with open(report_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        findings = data.get("findings", [])
        scanned_files = data.get("scanned_files", [])

        rows = ""
        for f in findings:
            rows += f"""
            <tr>
                <td><b style="color:red;">{f.get('severity')}</b></td>
                <td>{f.get('rule_id')}</td>
                <td>{os.path.basename(f.get('file'))}:{f.get('line')}</td>
                <td>{f.get('title')}</td>
            </tr>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SI-GUARD Təhlükəsizlik Hesabatı</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #121212; color: #fff; padding: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #333; padding: 10px; text-align: left; }}
                th {{ background: #1f1f1f; }}
                tr:nth-child(even) {{ background: #181818; }}
            </style>
        </head>
        <body>
            <h2>🛡️ SI-GUARD Təhlükəsizlik Skan Hesabatı</h2>
            <p> Tarix: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>📊 Skan edilən fayl sayı: {len(scanned_files)} | Tapılan zəiflik: {len(findings)}</p>
            <table>
                <tr>
                    <th>Səviyyə</th>
                    <th>Qaydası</th>
                    <th>Fayl & Məkan</th>
                    <th>Təsvir</th>
                </tr>
                {rows if rows else "<tr><td colspan='4'>Zəiflik tapılmadı</td></tr>"}
            </table>
        </body>
        </html>
        """

        output_path = "output_report.html"
        with open(output_path, "w", encoding="utf-8") as rf:
            rf.write(html_content)

        return f"📊 HTML Hesabat yaradıldı: `{output_path}`"
