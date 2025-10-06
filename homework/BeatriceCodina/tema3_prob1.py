'''# context
1) Create a class for parsing configuration of switch/router
 - class will support __enter__ and __exit__ methods for loading and closing configuration file
 - method get_config_block will return the configuration block that starts with the given words
   - example: in the config block below the argument for the method will be "interface Ethernet0/3"
                and the return value would be "no ip address\nshutdown"
 ```text
interface Ethernet0/3
 no ip address
 shutdown
```
'''
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
        found = False
        for line in self.lines:
            if line.strip() == start.strip():
                found = True
                continue
            if found:
                if line.startswith(" "):
                    block.append(line.strip())
                else:
                    break
        return "\n".join(block) if block else None

input = input("Introduceti linia de start a blocului: ")
with ConfigParser("testare_config.txt") as conf:
    block = conf.get_config_block(input)
    if block:
        print("Blocul găsit:\n", block)
    else:
        print("Nu s-a găsit blocul !")

