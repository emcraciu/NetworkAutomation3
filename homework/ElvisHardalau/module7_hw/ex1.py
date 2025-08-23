class Parser2:
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

    def reduce_config(self):
        self.lines = list(filter(lambda x: x.strip() != "!", self.lines))
        return self.lines

    def rename_interfaces(self, old_prefix="GigabitEthernet", new_prefix="Ethernet1/", start_index=1):
        def iface_gen():
            i = start_index
            while True:
                yield f"{new_prefix}{i}"
                i += 1

        gen = iface_gen()

        def replace(line):
            header = f"interface {old_prefix}"
            if line.startswith(header):
                return f"interface {next(gen)}"
            return line

        self.lines = list(map(replace, self.lines))
        return self.lines

with Parser2("config.txt") as cfg:
    cfg.reduce_config()
    cfg.rename_interfaces(old_prefix="GigabitEthernet", new_prefix="Ethernet1/", start_index=1)
    print("\n".join(cfg.lines))
