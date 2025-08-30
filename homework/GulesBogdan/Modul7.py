class Device():
    def __init__(self, filename: str):
        self.filename = filename
        self.device = None
        self.config = []

    def __enter__(self):
        self.device = open(self.filename, "r")
        for line in self.device:
            self.config.append(line.rstrip())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.device is not None:
            self.device.close()

    def get_config_block(self, start_line:str):
        right_one = ""
        start_ = False
        for i in self.config:
            if i == start_line:
                start_ = True
                continue
            if start_:
                if i.strip() == '!' or not i.startswith(" "):
                     break
                right_one += i + "\n"
        return right_one
    def reduce_config(self):
        self.config = list(filter(lambda n:n.strip()!="!",self.config))
    def rename_interfaces(self):
        def count():
            counter1 = 1
            counter2 = 1
            while True:
                yield f"Ethernet{counter1}/{counter2}"
                counter2 += 1
                if counter2==4:
                    counter1 += 1
                    counter2=0
        gen = count()
        def renamer(line):
            if line.startswith("interface GigabitEthernet") or line.startswith("interface Ethernet"):
                return f"interface {next(gen)}"
            return line

        self.config = list(map(renamer, self.config))

with Device("ex.txt") as d:
    print(d.config)
    d.reduce_config()
    print(d.get_config_block("interface Ethernet0/4"))
    d.rename_interfaces()
    print(d.config)

