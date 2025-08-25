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
                head_line = line
                i += 1
                block_lines = []
                while i < n:
                    next_line = self._lines[i].rstrip("\n")
                    if next_line.startswith(" ") or next_line.startswith("\t"):
                        block_lines.append(next_line.lstrip())
                        i += 1
                    else:
                        break
                return head_line + ("\n" + "\n".join(block_lines) if block_lines else "")
            i += 1
        return None

    def reduce_config(self):
        prev = False
        def keep(line):
            nonlocal prev
            if line.strip() == "!":
                if prev:
                    return False
                prev = True
                return True
            prev = False
            return True
        self._lines = list(filter(keep, self._lines))
        with open(self.path, "w", encoding=self.encoding, newline="") as f:
            f.writelines(self._lines)

    def rename_interfaces(self, old_prefix="GigabitEthernet0/", new_prefix="Ethernet1/", start=1):
        def gen():
            i = start
            while True:
                yield f"{new_prefix}{i}"
                i += 1
        g = gen()
        pref = "interface " + old_prefix
        def ren(line):
            if line.startswith(pref):
                eol = "\n" if line.endswith("\n") else ""
                return "interface " + next(g) + eol
            return line
        self._lines = list(map(ren, self._lines))
        with open(self.path, "w", encoding=self.encoding, newline="") as f:
            f.writelines(self._lines)
