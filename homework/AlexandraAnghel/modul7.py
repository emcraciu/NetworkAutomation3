class ConfigParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lines: list[str] = []

    def __enter__(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.lines = [line.rstrip("\n") for line in f]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lines = []

    def save(self, to_path: str | None = None) -> None:
        path = to_path or self.filepath
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines) + ("\n" if self.lines else ""))

    def get_config_block(self, start: str) -> list[str]:
        block: list[str] = []
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
    def reduce_config(self) -> None:
        prev_bang = False

        def keeper(line: str) -> bool:
            nonlocal prev_bang
            if line.strip() == "!":
                if prev_bang:
                    return False
                prev_bang = True
                return True
            prev_bang = False
            return True

        self.lines = list(filter(keeper, self.lines))

    def rename_interfaces(self, from_prefix: str = "GigabitEthernet0/", to_prefix: str = "Ethernet1/", start: int = 1) -> None:
        def gen_names(prefix: str, start_idx: int):
            i = start_idx
            while True:
                yield f"{prefix}{i}"
                i += 1

        names = gen_names(to_prefix, start)

        def mapper(line: str) -> str:
            stripped = line.lstrip()
            indent = line[: len(line) - len(stripped)]
            if stripped.startswith("interface ") and stripped[len("interface "):].startswith(from_prefix):
                return f"{indent}interface {next(names)}"
            return line

        self.lines = list(map(mapper, self.lines))


if __name__ == "__main__":
    cfg_path = "config.txt"

    with ConfigParser(cfg_path) as parser:
        print(parser.get_config_block("interface Ethernet0/3"))
        parser.reduce_config()
        parser.rename_interfaces(from_prefix="GigabitEthernet0/", to_prefix="Ethernet1/", start=1)
        parser.save("config_out.txt")
        print("config curățat și redenumit salvat în config_out.txt")
