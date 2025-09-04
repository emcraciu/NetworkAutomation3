import random
import threading
import time

# global_var = []
#
# def worker(name):
#     print(f"Thread {name} starting")
#     sleep_time = random.randint(1, 5)
#     time.sleep(sleep_time)
#     global_var.append(sleep_time)
#     print(f"Thread {name} finished")
#
# t1 = threading.Thread(target=worker, args=("A",))
# t2 = threading.Thread(target=worker, args=("B",))
# t1.start()
# t2.start()
# global_var.append(random.randint(1, 5))
# t1.join()
# t2.join()
# print("Both threads finished")
# print(global_var)



# counter = 0
# lock = threading.Lock()
#
# def increment():
#     global counter
#     for _ in range(5):
#         with lock:   # Lock acquired, prevents race conditions
#             counter += 1
#         # lock.acquire()
#         # counter += 1
#         # if counter == 7:
#         #     raise Exception('Failure happend')
#         # lock.release()
#
# threads = [threading.Thread(target=increment) for _ in range(5)]
# for t in threads: t.start()
# for t in threads: t.join()
# print("Final counter:", counter)


# counter = 0
# lock1 = threading.Lock()
# lock2 = threading.Lock()
#
# def increment():
#     global counter
#     for _ in range(100000):
#         with lock1:
#             with lock2:
#                 counter += 2
#
#         with lock2:
#             with lock1:
#                 counter -= 1
#         # lock.acquire()
#         # counter += 1
#         # if counter == 7:
#         #     raise Exception('Failure happend')
#         # lock.release()
#
# threads = [threading.Thread(target=increment) for _ in range(5)]
# for t in threads: t.start()
# for t in threads: t.join()
# print("Final counter:", counter)

# import threading
#
# lock = threading.RLock()
#
# def task():
#     lock.acquire()
#     print("Outer lock acquired")
#     lock.acquire()
#     print("Inner lock1 acquired")
#     lock.release()
#     lock.acquire()
#     print("Inner lock2 acquired")
#     lock.release()
#
#     lock.release()
#
# for i in range(10):
#     threading.Thread(target=task).start()


# def factorial(n):
#     if n == 0:
#         return 1
#     with lock:
#         return n * factorial(n - 1)
#
# threads = []
# for i in range(100):
#     thread = threading.Thread(target=factorial, args=(i,))
#     threads.append(thread)
#     thread.start()
#
# for thread in threads:
#     res = thread.join()
# # threading.Thread(target=factorial, args=(5,)).start()

# import threading, time
#
# sem = threading.Semaphore(2)  # max 2 threads allowed at once
#
# def worker(i):
#     with sem:
#         print(f"Thread {i} entered")
#         time.sleep(2)
#         print(f"Thread {i} exiting")
#
# for i in range(5):
#     threading.Thread(target=worker, args=(i,)).start()
#

# import threading, time
#
# event = threading.Event()
#
# def waiter():
#     print("Waiting for event to be set...")
#     event.wait()
#     print("Event detected, continuing")
#
# def setter():
#     time.sleep(2)
#     print("Setting event")
#     event.set()
#
# threading.Thread(target=waiter).start()
# threading.Thread(target=setter).start()

import threading, time

def background():
    while True:
        print("Background thread running")
        time.sleep(1)

t = threading.Thread(target=background, daemon=True)
t.start()

time.sleep(3)
print("Main program exiting")
time.sleep(3)