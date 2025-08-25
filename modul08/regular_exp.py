import re

import subprocess
process = subprocess.Popen(
    ['ip', 'addr', 'show'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
std_out, std_err = process.communicate()

pattern = re.compile(r'inet (\d{1,3}\.\d{1,3}\.[0-9]+\.\d+)/.+global')
result = re.findall(pattern, std_out)
print(result)

result = re.search(pattern, std_out)
print(result.group(1))

pattern = re.compile(r'inet (?P<name>\d{1,3}\.\d{1,3}\.[0-9]+\.\d+)/.+global')
result = re.search(pattern, std_out)
print(result.group('name'))

# pattern = re.compile(r'\s+inet (?P<name>\d{1,3}\.\d{1,3}\.[0-9]+\.\d+)/.+global')
# result = re.match(pattern, std_out)
# print(result.group('name'))