from pyats import aetest
from genie.testbed import load
import sys
import ftd1

# ---------- Unicon Dialog (fallback modern/legacy) ----------
HAS_DIALOG = False
try:
    from unicon.core.dialog import Dialog, Statement  # type: ignore
    HAS_DIALOG = True
except Exception:
    try:
        from unicon.eal.dialogs import Dialog, Statement  # type: ignore
        HAS_DIALOG = True
    except Exception:
        HAS_DIALOG = False

# set testbed-ul pentru FTD (nu schimba numele fisierului)
ftd1.set_testbed_file("ftd_testbed_bun.yaml")

TARGETS = []

# --------- UTILS ----------
def cidr_to_netmask(cidr: str):
    ip, prefix = cidr.split("/")
    p = int(prefix)
    mask = [(0xffffffff << (32 - p) >> i) & 0xff for i in (24,16,8,0)]
    return ip, ".".join(map(str, mask))

# --------- ROUTES ----------
def compute_static_routes():
    return {
        "IOU1": [
            "ip route 192.168.204.0 255.255.255.0 192.168.202.2",
            "ip route 192.168.203.0 255.255.255.0 192.168.200.3",
        ],
        "IOSV": [
            "ip route 192.168.201.0 255.255.255.0 192.168.202.1",
            "ip route 192.168.204.0 255.255.255.0 192.168.203.3",
        ],
        "CSR": [
            "ip route 192.168.201.0 255.255.255.0 192.168.203.2",
            "ip route 192.168.202.0 255.255.255.0 192.168.203.2",
        ],
    }

# --------- MGMT (global-config only) ----------
def mgmt_commands_global_config():
    return [
        "ip domain name cisco.com",
        "username cisco privilege 15 password 0 cisco",
        "enable secret cisco",
        "ip ssh version 2",
        "line vty 0 4",
        " login local",
        " transport input ssh",
        " exec-timeout 10 0",
    ]

def ensure_exec(dev):
    try:
        dev.execute("\x1A")  # CTRL+Z -> EXEC
    except Exception:
        pass
    try:
        dev.execute("terminal length 0")
    except Exception:
        pass

def generate_rsa_keys(dev):
    ensure_exec(dev)

    non_interactive = [
        "crypto key generate rsa general-keys modulus 2048",
        "crypto key generate rsa modulus 2048",
    ]
    for cmd in non_interactive:
        try:
            dev.execute(cmd)
            return
        except Exception:
            continue

    if HAS_DIALOG:
        dialog_2048 = Dialog([
            Statement(pattern=r"%\s*Do you really want to replace them\?\s*\[yes/no\]:\s*$", action="sendline(yes)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"[Pp]roceed with.*\?\s*\[yes/no\]:\s*$", action="sendline(yes)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"[Cc]hoose the size of the key modulus.*:\s*$", action="sendline(2048)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"[Hh]ow\s+many\s+bits.*modulus.*\[\d+\]:\s*$", action="sendline(2048)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"\[(?:512,)?768,?1024,?2048\].*:\s*$", action="sendline(2048)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"% You already have RSA keys.*", action=None, loop_continue=True, continue_timer=False),
        ])
        dialog_1024 = Dialog([
            Statement(pattern=r"%\s*Do you really want to replace them\?\s*\[yes/no\]:\s*$", action="sendline(yes)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"[Pp]roceed with.*\?\s*\[yes/no\]:\s*$", action="sendline(yes)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"[Cc]hoose the size of the key modulus.*:\s*$", action="sendline(1024)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"[Hh]ow\s+many\s+bits.*modulus.*\[\d+\]:\s*$", action="sendline(1024)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"\[(?:512,)?768,?1024,?2048\].*:\s*$", action="sendline(1024)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"% You already have RSA keys.*", action=None, loop_continue=True, continue_timer=False),
        ])
        for cmd in ("crypto key generate rsa general-keys", "crypto key generate rsa"):
            try:
                dev.execute(cmd, reply=dialog_2048, timeout=240)
                return
            except Exception:
                try:
                    dev.execute(cmd, reply=dialog_1024, timeout=240)
                    return
                except Exception:
                    continue

def save_config(dev):
    if HAS_DIALOG:
        confirm_yes = Dialog([
            Statement(pattern=r"Continue\?\s*\[no\]:\s*$", action="sendline(yes)", loop_continue=True, continue_timer=False),
            Statement(pattern=r"\[confirm\]\s*$", action="sendline()", loop_continue=True, continue_timer=False),
            Statement(pattern=r"Destination filename \[startup-config\]\?\s*$", action="sendline()", loop_continue=True, continue_timer=False),
            Statement(pattern=r"Overwrite\s+file.*\?\s*\[confirm\]\s*$", action="sendline()", loop_continue=True, continue_timer=False),
            Statement(pattern=r"\[yes/no\]:\s*$", action="sendline(yes)", loop_continue=True, continue_timer=False),
        ])
        try:
            dev.execute("copy running-config startup-config", reply=confirm_yes, timeout=120)
            return
        except Exception:
            try:
                dev.execute("write memory", reply=confirm_yes, timeout=120)
                return
            except Exception:
                pass
    try:
        dev.execute("copy running-config startup-config")
        return
    except Exception:
        try:
            dev.execute("write memory")
        except Exception:
            pass

# --------- AEtest ----------
class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_tb(self, section):
        testbed = load("testbed2.yaml")
        self.parent.parameters.update(testbed=testbed, targets=list(TARGETS))

class NetworkTest(aetest.Testcase):
    @aetest.setup
    def connect_all(self, testbed, targets, steps):
        self.devices = {}
        self.connected = []
        for name, dev in testbed.devices.items():
            if name == "UbuntuServer":
                continue
            if targets and name not in targets:
                continue
            with steps.start(f"Connect {name}", continue_=True) as step:
                try:
                    dev.connect(init_config_commands=[], learn_hostname=True, log_stdout=False)
                    try:
                        dev.execute("terminal length 0")
                    except Exception:
                        pass
                    self.devices[name] = dev
                    self.connected.append(name)
                    step.passed(f"Connected {name}")
                except Exception as e:
                    step.skipped(f"Fail connect {name}: {e}")

    @aetest.test
    def configure_hostname(self, steps):
        for name, dev in self.devices.items():
            if name not in self.connected:
                continue
            with steps.start(f"Hostname {name}", continue_=True) as step:
                dev.configure(f"hostname {name}")
                step.passed("ok")

    @aetest.test
    def configure_interfaces(self, steps):
        for name, dev in self.devices.items():
            if name not in self.connected:
                continue
            with steps.start(f"Interfaces {name}", continue_=True) as step:
                ifmap = dev.custom.get("interfaces", {})
                if not ifmap:
                    step.skipped("no interfaces in testbed"); continue
                cmds = []
                for ifn, idef in ifmap.items():
                    ipv4 = idef.get("ipv4")
                    if not ipv4:
                        continue
                    ip, mask = cidr_to_netmask(ipv4)
                    cmds += [
                        f"interface {ifn}",
                        f" ip address {ip} {mask}",
                        " no shutdown",
                    ]
                if cmds:
                    dev.configure(cmds)
                step.passed("ok")

    @aetest.test
    def configure_ssh_user(self, steps):
        for name, dev in self.devices.items():
            if name not in self.connected:
                continue
            with steps.start(f"Mgmt {name}", continue_=True) as step:
                dev.configure(mgmt_commands_global_config())
                generate_rsa_keys(dev)
                step.passed("ok")

    @aetest.test
    def configure_static_routes(self, steps):
        routes = compute_static_routes()
        for name, dev in self.devices.items():
            if name not in self.connected or name not in routes:
                continue
            with steps.start(f"Routes {name}", continue_=True) as step:
                dev.configure(routes[name])
                step.passed("ok")

    @aetest.cleanup
    def save_and_disconnect(self, steps):
        with steps.start("Save & disconnect", continue_=True) as step:
            for name, dev in self.devices.items():
                if name not in self.connected:
                    continue
                try:
                    save_config(dev)
                except Exception:
                    pass
                try:
                    dev.disconnect()
                except Exception:
                    pass
            step.passed("ok")

# --------- Extra Actions (menu) ----------
def ping_all(testbed):
    ub = testbed.devices.get("UbuntuServer")
    if not ub:
        print("UbuntuServer not found in testbed"); return
    try:
        ub.connect(init_config_commands=[], log_stdout=False)
    except Exception:
        pass
    print("=== Ping test ===")
    for devname, dev in testbed.devices.items():
        if devname == "UbuntuServer": continue
        ifmap = dev.custom.get("interfaces", {})
        for ifn, idef in ifmap.items():
            ipv4 = idef.get("ipv4")
            if not ipv4: continue
            ip = ipv4.split("/")[0]
            try:
                out = ub.execute(f"ping -c 2 -W 1 {ip}")
                status = "OK" if (" 0% packet loss" in out or " 0.0% packet loss" in out) else "FAIL"
            except Exception as e:
                status = f"ERROR {e}"
            print(f"{devname} {ifn} {ip} {status}")
    try:
        ub.disconnect()
    except Exception:
        pass

def delete_running(testbed):
    for name, dev in testbed.devices.items():
        if name == "UbuntuServer": continue
        try:
            dev.connect(init_config_commands=[], log_stdout=False)
        except Exception:
            pass
        try:
            print(f"--- wipe {name}")
            dev.execute("write erase")
            try:
                dev.configure([
                    "no ip ssh version 2",
                    "line vty 0 4",
                    " no login local",
                    " transport input none",
                ])
            except Exception:
                pass
        except Exception as e:
            print(f"{name}: {e}")
        try:
            dev.disconnect()
        except Exception:
            pass

def check_configured(testbed):
    for name, dev in testbed.devices.items():
        if name == "UbuntuServer": continue
        try:
            dev.connect(init_config_commands=[], log_stdout=False)
        except Exception:
            pass
        try:
            out = dev.execute("show running-config | include ^hostname|^ip domain name|^username cisco|^ip ssh")
            print(f"--- {name} ---\n{out.strip()}\n")
        except Exception as e:
            print(f"{name}: {e}")
        try:
            dev.disconnect()
        except Exception:
            pass

def menu():
    global TARGETS
    while True:
        print("\n=== MENU ===")
        print("1) Configure IOU1")
        print("2) Configure IOSV")
        print("3) Configure CSR")
        print("4) Configure All")
        print("5) Ping Test (UbuntuServer)")
        print("6) Delete all running-configs (no reload)")
        print("7) Check if configured")
        print("8) FTD first-time init (console)")
        print("9) FTD configure from topology (IF + routes)")
        print("0) Exit")
        ch = input("Select: ").strip()
        if ch == "0":
            break
        if ch == "5":
            tb = load("testbed2.yaml"); ping_all(tb); continue
        if ch == "6":
            tb = load("testbed2.yaml"); delete_running(tb); continue
        if ch == "7":
            tb = load("testbed2.yaml"); check_configured(tb); continue
        if ch == "8":
            ftd1.ftd_init_menu(); continue
        if ch == "9":
            ftd1.ftd_config_menu(); continue
        if ch not in {"1","2","3","4"}:
            continue

        if ch == "1": TARGETS = ["IOU1"]
        elif ch == "2": TARGETS = ["IOSV"]
        elif ch == "3": TARGETS = ["CSR"]
        elif ch == "4": TARGETS = ["IOU1", "IOSV", "CSR"]

        aetest.main()

if __name__ == "__main__":
    menu()
