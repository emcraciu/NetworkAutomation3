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



from multiprocessing import Pool

def square(x):
    print(f'{os.getpid()} calculating square of {x}')
    time.sleep(3)

    return x * x

if __name__ == "__main__":
    start = time.time()
    with Pool(4) as pool:
        results = pool.map(square, [1, 2, 3, 4, 5])
        print(results)
    end = time.time()
    print(end - start)