import time

# try:
#     file = open("test.txt","w")
#     file.write("hello world")
#     raise Exception
#     file.flush()
#     file.close()
#     file = open("test.txt","r")
#     print(file.read())
#     file.close()
#
# except Exception:
#     time.sleep(15) # can run for long time and file is not written to HD

try:
    with open("test.txt","w") as file:
        file.write("hello world")
        raise Exception
    print(response)
except Exception:
    time.sleep(15) # check for bug