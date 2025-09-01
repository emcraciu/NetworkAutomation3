import asyncio
import subprocess
import telnetlib3
import os

HOST = '92.81.55.146'
PORTS = [5168, 5170]



BACKUP_DIR = os.path.expanduser("/home/osboxes/Documents/Config_routers")
os.makedirs(BACKUP_DIR, exist_ok=True)

CONFIG_FILES = [
    os.path.join(BACKUP_DIR, f"{HOST}_{PORTS[0]}_backup.cfg"),
    os.path.join(BACKUP_DIR, f"{HOST}_{PORTS[1]}_backup.cfg"),
]
class TelnetConnection10:
    def __init__(self, host, port, config_file):
        self.host = host
        self.port = port
        self.config_file = config_file
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)
        await asyncio.sleep(1)

    def write(self, cmd):
        self.writer.write(cmd + '\r\n')

    async def get_running_config(self):
        self.write('terminal length 0')
        await asyncio.sleep(0.5)
        self.write('show running-config')
        await asyncio.sleep(2)
        config = await self.reader.read(20000)

        cleaned_lines = []
        for line in config.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('!'):
                continue
            if line.lower().startswith('current configuration'):
                continue
            if line.startswith('%'):
                continue
            if line.startswith('Building configuration'):
                continue
            if line.endswith('#') or line.endswith('>'):
                continue
            cleaned_lines.append(line)

        return cleaned_lines

    async def backup_config_to_pc(self):
        config_lines = await self.get_running_config()
        filename = os.path.join(BACKUP_DIR, f"{self.host}_{self.port}_backup.cfg")
        config_text = "\n".join(config_lines)

        proc = subprocess.run(
            ["tee", filename],
            input=config_text.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if proc.returncode == 0:
            print(f"Config salvat pe PC în {filename}")
        else:
            print(f"Eroare la salvare fișier {filename}: {proc.stderr.decode()}")

        return filename

    async def reset_factory(self):
        self.write('write erase')
        await asyncio.sleep(1)
        self.write('reload')
        await asyncio.sleep(5)

    async def apply_config(self):
        if not os.path.exists(self.config_file):
            print(f"Fișier lipsă: {self.config_file}")
            return

        with open(self.config_file, 'r') as f:
            saved_config = [line.rstrip() for line in f if line.strip() and not line.startswith('!')]

        running_config = await self.get_running_config()
        normalized_running = [self.normalize_line(line) for line in running_config]

        lines_to_apply = []
        current_interface = None

        for line in saved_config:
            normalized_line = self.normalize_line(line)

            if line.lower().startswith("interface "):
                current_interface = line
                if normalized_line not in normalized_running:
                    lines_to_apply.append(line)
                continue

            if current_interface:
                if normalized_line not in normalized_running:
                    if current_interface not in lines_to_apply:
                        lines_to_apply.append(current_interface)
                    lines_to_apply.append(line)

            else:
                if normalized_line not in normalized_running:
                    lines_to_apply.append(line)
        if current_interface:
            interface_lines = [l for l in running_config if l.startswith(current_interface) or l.startswith(" ")]
            normalized_interface_lines = [self.normalize_line(l) for l in interface_lines]
            if "no shutdown" not in normalized_interface_lines:
                lines_to_apply.append(" no shutdown")
        if not lines_to_apply:
            print(f"{self.config_file}: Routerul este deja configurat corect.")
            return

        self.write('conf t')
        await asyncio.sleep(1)
        for cmd in lines_to_apply:
            self.write(cmd)
            await asyncio.sleep(0.3)
        self.write('end')
        await asyncio.sleep(1)
        self.write('copy running-config startup-config')
        await asyncio.sleep(2)

        print(f"{self.config_file}: Configurația aplicată cu succes.")

    async def close(self):
        self.writer.close()

    def normalize_line(self, line):
        return ' '.join(line.strip().split())


async def configure_all():
    conns = [TelnetConnection10(HOST, port, cfg) for port, cfg in zip(PORTS, CONFIG_FILES)]
    await asyncio.gather(*(c.connect() for c in conns))
   #await asyncio.gather(*(c.backup_config_to_pc() for c in conns))
   #await asyncio.gather(*(c.reset_factory() for c in conns))
    await asyncio.gather(*(c.apply_config() for c in conns))

    await asyncio.gather(*(c.close() for c in conns))


if __name__ == "__main__":
    asyncio.run(configure_all())
