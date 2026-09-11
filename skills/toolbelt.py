import os
import re
import subprocess

class CyberToolbelt:
    def __init__(self, knowledge_base=None):
        self.kb = knowledge_base
        self.allowed_tools = {
            'nmap': 'Port ve xidmet skani',
            'curl': 'HTTP header analizi'
        }
