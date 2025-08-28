import multiprocessing as mp
import os
import time

# import os
# import time
#
#
# def worker(name):
#     time.sleep(10)
#     print(f"Worker {name} running in process id: {os.getpid()}")
#     time.sleep(10)
#     print(f"Worker {name} exiting")
#
#
# if __name__ == "__main__":
#     p1 = mp.Process(target=worker, args=("A",))
#     p2 = mp.Process(target=worker, args=("B",))
#     p1.start()
#     p2.start()
#     p1.join()
#     p2.join()
#     print("Both processes finished")



# from multiprocessing import Pool
#
# def square(x):
#     print(f'{os.getpid()} calculating square of {x}')
#     time.sleep(3)
#
#     return x * x
#
# if __name__ == "__main__":
#     start = time.time()
#     with Pool(4) as pool:
#         results = pool.map(square, [1, 2, 3, 4, 5])
#         print(results)
#     end = time.time()
#     print(end - start)


from multiprocessing import Process, Queue

def producer(q):
    for i in range(5):
        time.sleep(1)
        q.put(i)

def consumer(q):
    while not q.empty():
        item = q.get()
        print("Consuming:", item)
        time.sleep(2) # determines consumtion rate
        print("Consumed:", item)
    print(f"Consumer {os.getpid()} done")

if __name__ == "__main__":
    q = Queue()
    p1 = Process(target=producer, args=(q,))
    p2 = Process(target=consumer, args=(q,))
    p3 = Process(target=consumer, args=(q,))
    p1.start()
    time.sleep(3)
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()