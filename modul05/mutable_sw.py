class Switch:
    ports = []

    def add_port(self, port_name):
        self.ports.append(port_name)

        print(self.ports)

    def __init__(self):
        self.ports = []


sw = Switch()
print(sw.ports)

sw.add_port("Ethernet")

sw2 = Switch()
sw2.add_port("Ethernet5")

print(Switch.ports)
