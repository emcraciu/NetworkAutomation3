# Python Lesson: The `multiprocessing` Module

## 1. Introduction
The **`multiprocessing`** module allows Python programs to create and manage **separate processes**.  
Unlike threads, processes run in their **own memory space**, which avoids the Global Interpreter Lock (GIL) limitation.  

Common use cases:
- CPU-bound tasks (math, simulations, encryption).  
- Running tasks truly in parallel on multiple CPU cores.  

---

## 2. Creating a Process
```python
from multiprocessing import Process
import os

def worker(name):
    print(f"Worker {name} running in process id: {os.getpid()}")

if __name__ == "__main__":
    p1 = Process(target=worker, args=("A",))
    p2 = Process(target=worker, args=("B",))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Both processes finished")
```
## 3. Using a Pool of Processes

A Pool manages a group of worker processes.
```python
from multiprocessing import Pool

def square(x):
    return x * x

if __name__ == "__main__":
    with Pool(4) as pool:
        results = pool.map(square, [1, 2, 3, 4, 5])
        print(results)
```
## 4. Shared Data and Queues

Use Queue or Value/Array for inter-process communication.
```python
from multiprocessing import Process, Queue

def producer(q):
    for i in range(5):
        q.put(i)

def consumer(q):
    while not q.empty():
        item = q.get()
        print("Consumed:", item)

if __name__ == "__main__":
    q = Queue()
    p1 = Process(target=producer, args=(q,))
    p2 = Process(target=consumer, args=(q,))
    p1.start(); p1.join()
    p2.start(); p2.join()

```
## 5. Conclusion

The multiprocessing module provides true parallelism in Python for CPU-intensive tasks.
It is especially useful for programs that need to leverage multiple CPU cores.

## 
6. References

Python Docs: multiprocessing 

Real Python: Intro to Python Multiprocessing