from pyats import aetest, topology
import json
import re
import matplotlib
matplotlib.use("Agg")  # no GUI backend
import matplotlib.pyplot as plt
import os, datetime, subprocess
import shutil

SERVER_IP = "192.168.200.1"

def parse_iperf_text(output):
    import os, datetime, re, subprocess
    import matplotlib.pyplot as plt

    intervals = []
    bandwidths = []

    regex = re.compile(r"(\d+\.\d+)-(\d+\.\d+)\s+sec\s+[\d\.]+\s+\w+Bytes\s+([\d\.]+)\s+(\wbits/sec)")

    for line in output.splitlines():
        m = regex.search(line)
        if m:
            start, end, value, unit = m.groups()
            bw_mbps = float(value)
            if "Kbits" in unit:
                bw_mbps /= 1000
            elif "Gbits" in unit:
                bw_mbps *= 1000
            t = (float(start) + float(end)) / 2
            intervals.append(t)
            bandwidths.append(bw_mbps)

    if not intervals:
        print(" No throughput lines parsed.")
        return None

    # 🔹 Sort data by time so the line never goes backwards
    data = sorted(zip(intervals, bandwidths), key=lambda x: x[0])
    intervals, bandwidths = zip(*data)

    # save on ubuntu
    BASE_DIR = "/home/osboxes/PycharmProjects/ProjectPyNet3/results"
    os.makedirs(BASE_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    png_path = os.path.join(BASE_DIR, "iperf_latest.png")
    log_path = os.path.join(BASE_DIR, f"iperf_{timestamp}.log")

    # Save raw iperf output
    with open(log_path, "w") as f:
        f.write(output)

    # Plot throughput
    plt.figure(figsize=(8, 4))
    plt.plot(intervals, bandwidths, linestyle="-")
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (Mbps)")
    plt.title("iPerf3 Throughput vs Time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()

    # === Copie în static/results pentru Flask ===
    STATIC_DIR = "/tmp/pycharm_project_446/Project/Project/static/results"
    os.makedirs(STATIC_DIR, exist_ok=True)

    copy_path = os.path.join(STATIC_DIR, "iperf_latest.png")
    shutil.copy(png_path, copy_path)

    print(f"Copied to Flask static: {copy_path}")

    print(f"Saved plot: {png_path}")
    print(f"Saved raw log: {log_path}")

    # Auto-open the PNG (Linux)
    try:
        subprocess.Popen(["xdg-open", png_path],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f" Could not auto-open image: {e}")

    return png_path

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, steps):
        tb = topology.loader.load("ubuntu_docker1_tesbed.yaml")
        self.parent.parameters.update(tb=tb)


class ConfigureUbuntu(aetest.Testcase):
    @aetest.setup
    def connect(self, steps):
        tb = self.parent.parameters.get("tb")
        self.dev = tb.devices.UbuntuDocker1
        self.dev.connect(via="cli", log_stdout=True)

    @aetest.test
    def set_ip_address(self, steps):
        cmds = [
            "ip addr flush dev eth0",
            "ip addr add 192.168.210.1/24 dev eth0",
            "ip link set eth0 up",
            "ip route add default via 192.168.210.10"
        ]
        for cmd in cmds:
            with steps.start(f"Run: {cmd}"):
                output = self.dev.execute(cmd, timeout=10)
                print(output)

    @aetest.test
    def run_iperf_client(self, steps):
        cmd = f"iperf3 -c {SERVER_IP} -t 10"
        with steps.start(f"Run iperf client to {SERVER_IP}"):
            output = self.dev.execute(cmd, timeout=40)
            print("\n===== Raw iperf3 Output =====")
            print(output)
            print("================================")

            # Generate plot + save log
            path = parse_iperf_text(output)
            if path:
                self.dev.log.info(f"Plot generated at {path}")
            else:
                self.dev.log.error(" Failed to parse iperf3 output for plotting.")




if __name__ == "__main__":
    aetest.main()
