class Device():
    def __init__(self, filename: str):
        self.filename = filename
        self.device=None
        self.config=[]
    def __enter__(self):
        self.device = open(self.filename, "r")
        for line in self.device:
            line = line.rstrip()
            self.config.append(line)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.device is not None:
            self.device.close()
    def get_config_block(self,start_line:str):
        right_one = ""
        start_=False
        for i in self.config:
            if i == start_line:
                start_=True
                continue
            if start_:
                if i.strip() == '!' or not i.startswith(" "):
                     break
                right_one=right_one+i+ "\n"
        return right_one

with Device("ex.txt") as d:
    print(d.get_config_block("interface Ethernet0/4"))








