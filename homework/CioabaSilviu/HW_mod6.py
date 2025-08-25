class ConfigParser:
    def __init__(self, encoding="utf-8"):
        self.path = "running_config.txt"
        self.encoding = encoding
        self._fh = None
        self._lines = []

    def __enter__(self):
        self._fh = open(self.path, "r", encoding=self.encoding, newline="")
        self._lines = self._fh.readlines()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._fh:
            self._fh.close()
        self._fh = None

    def get_config_block(self, heading):
        i = 0
        n = len(self._lines)
        while i < n:
            line = self._lines[i].rstrip("\n")
            if line.startswith(heading) and (len(line) == len(heading) or line[len(heading)] in (" ", "\t")):
                i += 1
                block_lines = []
                while i < n:
                    next_line = self._lines[i].rstrip("\n")
                    if next_line.startswith(" ") or next_line.startswith("\t"):
                        block_lines.append(next_line.lstrip())
                        i += 1
                    else:
                        break
                return "\n".join(block_lines) if block_lines else ""
            i += 1
        return None

#with ConfigParser() as cfg:
#    print(cfg.get_config_block("interface Ethernet0/3"))
