import sys
import subprocess
import os
from pathlib import Path
from sender_email import send_email

BASE_DIR = Path(__file__).resolve().parent

DEVICES = {
    "1": ("iou1_config.py", "iou1_testbed.yaml"),
    "2": ("iosv_config.py", "iosv_testbed.yaml"),
    "3": ("csr_config.py", "csr_testbed.yaml"),
    "4": ("ubuntu_config.py", "ftd_testbed.yaml"),
    "5": ("ospf_config.py", "testbed.yaml"),
}

def run_test(script, testbed):
    script_path = BASE_DIR / script
    testbed_path = BASE_DIR / testbed

    if not script_path.exists():
        msg = f" Script {script} does not exist!"
        print(msg)
        send_email(" Automation Test Error", msg)
        return
    if not testbed_path.exists():
        msg = f" Testbed {testbed} does not exist!"
        print(msg)
        send_email(" Automation Test Error", msg)
        return

    env = dict(**os.environ)
    env["TESTBED"] = str(testbed_path)

    try:
        subprocess.run([sys.executable, str(script_path)], check=True, env=env)
        msg = f" Test {script} ran successfully on {testbed}"
        print(msg)
        send_email(" Automation Test OK", msg)

    except subprocess.CalledProcessError as e:
        msg = f" Test {script} failed: {e}"
        print(msg)
        send_email(" Automation Test Failed", msg)

def main():
    while True:
        print("\n=== DEVICE CONFIG MENU ===")
        print("1. Run IOU1")
        print("2. Run IOSv")
        print("3. Run CSR1000v")
        print("4. Run Ubuntu Host")
        print("5. Configure OSPF on devices")
        print("0. Exit")

        opt = input("Choose an option: ").strip()

        if opt == "0":
            print("Bye")
            break

        if opt in DEVICES:
            script, testbed = DEVICES[opt]
            run_test(script, testbed)
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
