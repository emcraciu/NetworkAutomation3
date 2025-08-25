'''
# Using map/filter
1) Extend the functionality for class in homework 6 with 2 methods
    - method1 "reduce_config" will use filter and change the configuration file to remove the extra "!"
    - method2 "rename_interfaces" will use map and allow the changing of the interface names in the configuration file
      - example  GigabitEthernet0/0 > Ethernet1/1, GigabitEthernet0/1 > Ethernet1/2 ...
      - use generator to produce the incremental interface names
'''


def new_interface_names():
    i = 1
    j = 1
    while True:
        yield f"Ethernet{i}/{j}"
        j = j + 1
        if j > 6:
            j = 1
            i = i + 1


class ConfigParser:
    def __init__(self, filename: str):
        self.filename = filename

    def __enter__(self):
        with open(self.filename, "r") as f:
            self.lines = [line.rstrip("\n") for line in f]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def get_config_block(self, start: str) -> str | None:
        block = []
        inside = False
        for line in self.lines:
            if line.strip() == start.strip():
                inside = True
                continue
            if inside:
                if line.startswith(" "):
                    block.append(line.strip())
                else:
                    break
        return "\n".join(block) if block else None

    def reduce_config(self):
        self.lines = list(filter(lambda line: line.strip() != "!", self.lines))

    def rename_interfaces(self):
        gen_int = new_interface_names()

        def replace(line):
            if line.startswith("interface"):
                return f"interface {next(gen_int)}"
            return line

        self.lines = list(map(replace, self.lines))


with ConfigParser("testare_config.txt") as conf:
    print("Configuratia originala inainte de modificari: ")
    print("\n".join(conf.lines))

    conf.reduce_config()
    print("\nConfiguratia dupa eliminarea '!': ")
    print("\n".join(conf.lines))

    conf.rename_interfaces()
    print("\nConfiguratia cu interfețele redenumite: ")
    print("\n".join(conf.lines))

    # Exemplu bloc
    input_line = input("Introduceți linia de start a blocului: ")
    block = conf.get_config_block(input_line)
    if block:
        print("\nBlocul găsit:\n", block)
    else:
        print("\nNu s-a găsit blocul!")
