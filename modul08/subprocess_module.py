import subprocess
import os

# result  = subprocess.run(["dir"], shell=True)
# print(result)
# result  = subprocess.run(["ping", '8.8.8.8'])
# print(result)
# result  = subprocess.run(["notepad"])
# print(result)
#
# path = os.path.join('C:\\Users\\ozy24\\PycharmProjects\\NetworkAutomation3\\modul07', 'ex1.py')
# print(path)

# result = subprocess.run(["python.exe", path], capture_output=True, text=True)
#
# print(result.stdout)
# print(result.stderr)
# #
#
# try:
#     result = subprocess.run(["python.exe", path], capture_output=True, text=True, check=True)
# except subprocess.CalledProcessError as e:
#     print(e)
# print(result.stdout)
# print(result.stderr)
# #

# Popen

process = subprocess.Popen(
    ['echo', 'test'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True,
    text=True,
)
std_out, std_err = process.communicate()
print(type(std_out))
print(type(std_err))