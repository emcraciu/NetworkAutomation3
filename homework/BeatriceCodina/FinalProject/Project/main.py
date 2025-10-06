import sys
import subprocess
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


DEVICES = {
    "1": ("iou1_config.py", "iou1_testbed.yaml"),
    "2": ("iosv_config.py", "iosv_testbed.yaml"),
    "3": ("csr_config.py", "csr_testbed.yaml"),
    "4": ("ftd_initial_config.py", "ftd_testbed.yaml"),
    "5": ("ftd_swagger.py", "testbed.yaml"),
    "6": ("try.py", "ftd_testbed.yaml"), #!!!!!!!!!!!!!!!!!
    "7": ("ftd_dhcp.py", "ftd_testbed.yaml"),
    "8": ("ubuntu_configWithIperf.py", "testbed.yaml"),
    "9": ("ubuntu_docker1_config.py", "ubuntu_docker1_tesbed.yaml"),
}

PY_FULL = "/home/osboxes/.virtualenvs/Project/bin/python"
PW_MOD  = ["-m", "playwright"]
CACHE   = Path("/home/osboxes/.cache/ms-playwright")

def env_for_playwright():
    env = os.environ.copy()
    env["HOME"] = "/home/osboxes"
    env["XDG_CACHE_HOME"] = "/home/osboxes/.cache"
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(CACHE)
    return env

def ensure_chromium_ready():
    """Verifică și instalează Chromium + deps dacă lipsesc"""
    if not any(CACHE.glob("chromium-*")):
        print("[info] Chromium lipsește — instalez cu deps...")
        subprocess.run([PY_FULL, *PW_MOD, "install", "--with-deps", "chromium"],
                       check=True, env=env_for_playwright())
    else:
        print("[info] Chromium deja instalat în cache")

def run_script(script, testbed, use_full_path=False, env=None):
    print(f"=== Running {script} with {testbed} ===")
    if use_full_path:
        subprocess.run([PY_FULL, script, testbed], check=True, env=env)
    else:
        subprocess.run([sys.executable, script, testbed], check=True)

def run_test(script, testbed):
    script_path = BASE_DIR / script
    testbed_path = BASE_DIR / testbed

    if not script_path.exists():
        print(f" Scriptul {script} nu există!")
        return
    if not testbed_path.exists():
        print(f" Testbed-ul {testbed} nu există!")
        return

    env = dict(**os.environ)
    env["TESTBED"] = str(testbed_path)

    try:
        subprocess.run([sys.executable, str(script_path)], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f" Test {script} failed: {e}")


def main():
    while True:
        print("\n=== MENIU DEVICE CONFIG ===")
        print("1. Rulează IOU1")
        print("2. Rulează IOSv")
        print("3. Rulează CSR1000v")
        print("4. Rulează FTD initial config")
        print("5. Ruleaza FTD swagger")
        print("6. Ruleaza FTD next next")
        print("7. Ruleaza FTD dhcp")
        print("8. Rulează Ubuntu Host with iperf")
        print("9. Ruleaza Ubuntu Docker 1")
        print("0. Ieșire")

        opt = input("Alege opțiunea: ").strip()

        if opt == "0":
            print("Bye ")
            break

        elif opt == "6":
            ensure_chromium_ready()
            run_script("try.py", "ftd_testbed.yaml", use_full_path=True, env=env_for_playwright())

        elif opt in DEVICES:
            script, testbed = DEVICES[opt]
            run_test(script, testbed)
        else:
            print("Opțiune invalidă!")


if __name__ == "__main__":
    main()
