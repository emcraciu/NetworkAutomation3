# Andrei Rad
# extract ip addr from ubuntu:
import subprocess
process = subprocess.Popen(
    ['ip', 'addr', 'show'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
std_out, std_err = process.communicate()
# print(std_out, std_err)
for line in std_out.splitlines():
    if 'inet ' in line:
        if '127' not in line:
            print(line.split()[1].split("/")[0])
