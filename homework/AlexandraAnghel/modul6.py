class ConfigParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lines = []

    def __enter__(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.lines = [line.rstrip("\n") for line in f]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lines = []

    def get_config_block(self, start: str) -> list[str]:
        block = []
        capture = False
        for line in self.lines:
            if line.strip().startswith(start):
                capture = True
                continue
            if capture:
                if line[:1].isspace():
                    block.append(line.strip())
                else:
                    break
        return block

if __name__ == "__main__":
    with ConfigParser("config.txt") as parser:
        block = parser.get_config_block("interface Ethernet0/3")
        print(block)
