class Parser:
    def __init__(self, filename):
        self.filename = filename
        self.lines = []

    def __enter__(self):
        with open(self.filename) as file:
            self.lines = file.read().splitlines()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lines = []

    def get_config_block(self, header):
        for i, line in enumerate(self.lines):
            if line.startswith(header):
                block = []
                for j in range(i + 1, len(self.lines)):
                    block.append(self.lines[j].strip())
                return "\n".join(block)
        return None

with Parser("config.txt") as cfg:
    print(cfg.get_config_block("interface Ethernet0/3"))