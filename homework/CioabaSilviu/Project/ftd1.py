# ftd1.py

from genie.testbed import load
from ipaddress import IPv4Interface, ip_interface, IPv4Address
import random
import string

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

# pyATS SecretString safe-handling
def _normalize_password(p):
    if p is None:
        return None
    if isinstance(p, str):
        return p
    for attr in ("to_plaintext", "reveal", "get_secret_value"):
        try:
            val = getattr(p, attr)()
            if isinstance(val, str) and val:
                return val
        except Exception:
            pass
    for attr in ("value", "string", "_plain", "_string"):
        try:
            val = getattr(p, attr)
            if isinstance(val, str) and val:
                return val
        except Exception:
            pass
    return None

TESTBED_FILE = "ftd_testbed_bun.yaml"

def set_testbed_file(path: str):
    global TESTBED_FILE
    TESTBED_FILE = path

# ---------- Helpers ----------
def _ip_mask_from_any(val):
    if isinstance(val, IPv4Interface):
        return str(val.ip), str(val.network.netmask)
    iface = ip_interface(str(val))
    return str(iface.ip), str(iface.network.netmask)

def cidr_to_ip_mask(cidr):
    return _ip_mask_from_any(cidr)

def ip_net_gateway(val):
    iface = val if isinstance(val, IPv4Interface) else ip_interface(str(val))
    gw = IPv4Address(int(iface.network.network_address) + 1)
    return str(gw)

def get_tb():
    return load(TESTBED_FILE)

def first_ftd(tb):
    for name, dev in tb.devices.items():
        osn = str(getattr(dev, "os", "")).lower()
        typ = str(getattr(dev, "type", "")).lower()
        if osn in ("ftd", "firepower", "asa") or "ftd" in typ or "firepower" in typ:
            return name, dev
    return None, None

def _pick_connection_name(dev):
    conns = list(getattr(dev, "connections", {}).keys())
    for pref in ("telnet", "ssh"):
        if pref in conns:
            return pref
    return conns[0] if conns else None

def _cleanup_connection_info(dev, conn_name):
    ci = dev.connections[conn_name]
    try:
        if isinstance(ci, dict):
            ci.pop('class', None)
            ci.setdefault('protocol', 'telnet')
        else:
            try:
                del ci['class']  # type: ignore[index]
            except Exception:
                pass
            try:
                getattr(ci, 'protocol')
            except Exception:
                ci['protocol'] = 'telnet'  # type: ignore[index]
    except Exception:
        pass

def _connect(dev):
    conn = _pick_connection_name(dev)
    if not conn:
        raise RuntimeError(f"{dev.name}: no connection defined")
    _cleanup_connection_info(dev, conn)
    dev.connect(
        via=conn,
        learn_hostname=False,
        log_stdout=False,
        init_exec_commands=[],
        init_config_commands=[],
        connection_timeout=300,
    )
    return conn

def _enter_enable(dev):
    en_pw = _normalize_password(dev.credentials.get("enable", {}).get("password", None))
    if HAS_DIALOG and en_pw:
        dlg = Dialog([Statement(r"[Pp]assword:\s*$", action=f"sendline({en_pw})")])
        try:
            dev.execute("enable", reply=dlg, timeout=30)
        except Exception:
            pass
    else:
        try:
            dev.execute("enable")
        except Exception:
            pass
    try:
        dev.execute("terminal pager 0")
    except Exception:
        pass

# ---------- Password utils ----------
SPECIAL_CHARS = "@#*-_+!"

def validate_password(pw: str) -> bool:
    if not pw or len(pw) < 8:
        return False
    if not any(c.islower() for c in pw): return False
    if not any(c.isupper() for c in pw): return False
    if not any(c.isdigit() for c in pw): return False
    if not any(c in SPECIAL_CHARS for c in pw): return False
    cur = 1
    for a, b in zip(pw, pw[1:]):
        if a == b:
            cur += 1
            if cur > 2: return False
        else:
            cur = 1
    for i in range(len(pw) - 3):
        seg = pw[i:i+4]
        vals = [ord(c) for c in seg]
        diffs = [vals[j+1] - vals[j] for j in range(3)]
        if all(d == 1 for d in diffs): return False
        if all(d == -1 for d in diffs): return False
    return True

def generate_compliant_password(length: int = 12) -> str:
    if length < 8: length = 8
    pool = string.ascii_letters + string.digits + SPECIAL_CHARS
    for _ in range(300):
        cand = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
            random.choice(SPECIAL_CHARS),
        ]
        while len(cand) < length:
            cand.append(random.choice(pool))
        random.shuffle(cand)
        pw = "".join(cand)
        if validate_password(pw):
            return pw
    base = "Aa1@" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length-4))
    return base if validate_password(base) else "Aa1@Z9yX7wV"

# ---------- First-time init ----------
def ftd_first_time_init(dev, tb, gw_default="192.168.200.6"):
    if not HAS_DIALOG:
        return

    # desired password from testbed (can be SecretString)
    tb_pwd_obj = dev.credentials.get("default", {}).get("password", None)
    raw_desired_pwd = _normalize_password(tb_pwd_obj) or "Cisco@135"
    desired_pwd = raw_desired_pwd if validate_password(raw_desired_pwd) else generate_compliant_password(12)
    dev.credentials.setdefault("default", {})["password"] = desired_pwd

    initial_user = "admin"
    initial_pwd  = "Admin123"

    mgmt_if = "Management1/1"
    if mgmt_if in dev.interfaces and getattr(dev.interfaces[mgmt_if], "ipv4", None):
        mgmt_ip_cidr = dev.interfaces[mgmt_if].ipv4
        mgmt_ip, mgmt_mask = cidr_to_ip_mask(mgmt_ip_cidr)
        gw = ip_net_gateway(mgmt_ip_cidr)
    else:
        mgmt_ip, mgmt_mask = "192.168.200.4", "255.255.255.0"
        gw = gw_default

    saved_user_obj = dev.credentials.get("default", {}).get("username", None)
    saved_pwd_obj  = dev.credentials.get("default", {}).get("password", None)
    saved_user = saved_user_obj if isinstance(saved_user_obj, str) else "admin"
    saved_pwd  = _normalize_password(saved_pwd_obj) or desired_pwd

    dev.credentials["default"]["username"] = initial_user
    dev.credentials["default"]["password"] = initial_pwd

    def _send_new(spawn, context, session):
        spawn.sendline(desired_pwd)

    def _send_confirm(spawn, context, session):
        spawn.sendline(desired_pwd)

    def _resend_both(spawn, context, session):
        # when device says "Passwords do not match.", it will re-ask:
        # send desired twice back-to-back to satisfy new+confirm quickly
        spawn.sendline(desired_pwd)
        spawn.sendline(desired_pwd)

    d = Dialog([
        # Login
        Statement(r"(?i)(firepower|ftd).*login:\s*$", action=f"sendline({initial_user})", loop_continue=True, continue_timer=False),
        Statement(r"(?i)^Password:\s*$",              action=f"sendline({initial_pwd})",  loop_continue=True, continue_timer=False),

        # EULA / paging / accepts
        Statement(r"Press\s*<ENTER>\s*to\s*display\s*the\s*EULA:.*", action="sendline()", loop_continue=True, continue_timer=False),
        Statement(r"--More--",                                       action="sendline()", loop_continue=True, continue_timer=False),
        Statement(r"Press\s*ENTER\s*to\s*continue.*",                action="sendline()", loop_continue=True, continue_timer=False),
        Statement(r"(?i)Please enter 'YES' or press <ENTER>.*",      action="sendline()", loop_continue=True, continue_timer=False),
        Statement(r"(?i)(Type|Enter)\s+YES\s+to\s+continue.*",       action="sendline(YES)", loop_continue=True, continue_timer=False),
        Statement(r"\[yes/no\]\s*:\s*$",                             action="sendline(yes)", loop_continue=True, continue_timer=False),

        # New password flow (robust)
        Statement(r"(?i)^Enter current password:\s*$",               action=f"sendline({initial_pwd})", loop_continue=True, continue_timer=False),
        Statement(r"(?i)^Enter new password:\s*$",                   action=_send_new,      loop_continue=True, continue_timer=False),
        Statement(r"(?i)^(Confirm|Re-enter) new password:\s*$",      action=_send_confirm,  loop_continue=True, continue_timer=False),
        Statement(r"(?i)Passwords do not match\.\s*$",               action=_resend_both,   loop_continue=True, continue_timer=False),
        Statement(r"(?i)Password must be.*",                         action=_send_new,      loop_continue=True, continue_timer=False),
        Statement(r"(?i)Invalid.*password.*",                        action=_send_new,      loop_continue=True, continue_timer=False),

        # IPv4/IPv6 wizard
        Statement(r"Do you want to configure IPv4\?.*",              action="sendline()",   loop_continue=True, continue_timer=False),
        Statement(r"Do you want to configure IPv6\?.*",              action="sendline()",   loop_continue=True, continue_timer=False),
        Statement(r"Configure IPv4 via DHCP or manually\?.*",        action="sendline(manual)", loop_continue=True, continue_timer=False),
        Statement(r"Enter an IPv4 address.*:\s*$",                   action=f"sendline({mgmt_ip})",   loop_continue=True, continue_timer=False),
        Statement(r"Enter an IPv4 netmask.*:\s*$",                   action=f"sendline({mgmt_mask})", loop_continue=True, continue_timer=False),
        Statement(r"Enter a fully qualified hostname.*:\s*$",        action="sendline()",   loop_continue=True, continue_timer=False),
        Statement(r"Enter the IPv4 default gateway.*:\s*$",          action=f"sendline({gw})",        loop_continue=True, continue_timer=False),
        Statement(r"Enter a comma-separated list of DNS servers.*:\s*$",   action="sendline()", loop_continue=True, continue_timer=False),
        Statement(r"Enter a comma-separated list of search domains.*:\s*$", action="sendline()", loop_continue=True, continue_timer=False),
        Statement(r"Manage the device locally\?.*:\s*$",             action="sendline()",   loop_continue=True, continue_timer=False),

        # Generic yes/continue
        Statement(r"(?i)(Proceed|Continue).*\[yes/no\].*",           action="sendline(yes)", loop_continue=True, continue_timer=False),
        Statement(r"(?i)(Accept|Agree).*\[yes/no\].*",               action="sendline(yes)", loop_continue=True, continue_timer=False),
        Statement(r"\[Press any key to continue\].*",                action="sendline()",   loop_continue=True, continue_timer=False),
    ])

    try:
        _connect(dev)
        dev.execute("", reply=d, timeout=1800)
    finally:
        try:
            dev.credentials["default"]["username"] = saved_user if saved_user else "admin"
            dev.credentials["default"]["password"] = saved_pwd if saved_pwd else desired_pwd
        except Exception:
            pass
        try:
            dev.disconnect()
        except Exception:
            pass

# ---------- Configure interfaces ----------
def ftd_configure_interfaces_from_topology(dev, tb):
    _connect(dev)
    _enter_enable(dev)
    cmds = []

    tdev = tb.devices[dev.name]
    for ifn, idef in tdev.interfaces.items():
        if ifn == "Management1/1":
            continue
        ipv4 = getattr(idef, "ipv4", None)
        if not ipv4:
            continue

        ip, mask = _ip_mask_from_any(ipv4)
        alias = getattr(idef, "alias", None) or ifn.lower().replace("/", "_")

        if ifn.endswith("0/0"):
            sec = 0
        elif ifn.endswith("0/1"):
            sec = 100
        else:
            sec = 50

        cmds += [
            "configure terminal",
            f"interface {ifn}",
            f" nameif {alias}",
            f" security-level {sec}",
            f" ip address {ip} {mask}",
            " no shutdown",
            " exit",
        ]

    if cmds:
        dev.configure(cmds)
    try:
        dev.disconnect()
    except Exception:
        pass

# ---------- Add default routes ----------
def ftd_add_default_routes(dev, tb):
    tdev = tb.devices[dev.name]
    _connect(dev)
    _enter_enable(dev)

    cmds = ["configure terminal"]
    for ifn, idef in tdev.interfaces.items():
        if ifn == "Management1/1":
            continue
        ipv4 = getattr(idef, "ipv4", None)
        if not ipv4:
            continue
        alias = getattr(idef, "alias", None) or ifn.lower().replace("/", "_")
        gw = ip_net_gateway(ipv4)
        cmds.append(f"route {alias} 0.0.0.0 0.0.0.0 {gw} 1")

    if len(cmds) > 1:
        dev.configure(cmds)
    try:
        dev.disconnect()
    except Exception:
        pass

# ---------- Menus (single FTD) ----------
def ftd_init_menu():
    tb = get_tb()
    name, dev = first_ftd(tb)
    if not dev:
        print("No FTD device found in testbed.")
        return
    print(f"FTD first-time init on '{name}'")
    ftd_first_time_init(dev, tb, gw_default="192.168.200.6")

def ftd_config_menu():
    tb = get_tb()
    name, dev = first_ftd(tb)
    if not dev:
        print("No FTD device found in testbed.")
        return
    print(f"FTD configure from topology on '{name}'")
    ftd_configure_interfaces_from_topology(dev, tb)
    ftd_add_default_routes(dev, tb)
