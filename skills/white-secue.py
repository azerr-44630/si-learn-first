import os
import json
from typing import Dict, Any

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
except ImportError:
    print("[!] jinja2 not installed. Run: pip install jinja2")
    raise

class WhiteSecue:
    """SI-GUARD White-Secue Module - Exploit Generation & Validation"""
    
    def __init__(self):
        self.name = "white-secue"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.templates_dir = os.path.join(base_dir, "..", "data", "exploit_templates")
        self.output_dir = os.path.join(base_dir, "..", "output", "exploits")
        
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
            
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def run(self, target_info: Dict[str, Any]) -> str:
        vuln_type = target_info.get("vulnerability_type", "unknown")
        target_os = target_info.get("target_os", "linux")
        template_name = f"{vuln_type}_{target_os}.py.j2"
        
        try:
            template = self.jinja_env.get_template(template_name)
            rendered = template.render(**target_info)
            return self._save(rendered, target_info)
        except TemplateNotFound:
            return f"[!] Template missing: {template_name}"
        except Exception as e:
            return f"[!] White-Secue generation failed: {str(e)}"
            
    def _save(self, code: str, ctx: Dict[str, Any]) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        cve = ctx.get("cve_id", "custom")
        path = os.path.join(self.output_dir, f"ws_{cve}.py")
        with open(path, 'w') as f:
            f.write(code)
        return f"[+] White-Secue saved: {path}"
