class TerminalUI:
    def __init__(self):
        self.colors = {
            'reset': '\033[0m',
            'green': '\033[92m',
            'blue': '\033[94m',
            'cyan': '\033[96m',
            'magenta': '\033[95m'
        }

    def print_header(self):
        c = self.colors
        print(f"{c['cyan']}==========================================")
        print(f" SI-LEAR-FIRST - Autonomous Cyber Agent")
        print(f"=========================================={c['reset']}")
