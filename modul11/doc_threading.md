# Module11: The `threading` Module

## 1. Introduction
The **`threading`** module allows Python programs to run multiple threads **within the same process**.  
Threads share memory space but are subject to the **Global Interpreter Lock (GIL)**.  


*PEP 703: Making the GIL Optional* introduces a build configuration mode where the interpreter can be compiled without a GIL (--disable-gil). 
This results in a free-threaded build where multiple threads can execute Python bytecode truly in parallel.
These free-threaded builds typically use a different executable (e.g., python3.13t) and are not the default. 
They are experimental and come with caveats such as:

- potential compatibility issues with existing C extension modules.
- a significant single-threaded performance penalty.
- ongoing development to stabilize this mode.

Best suited for:
- I/O-bound tasks (networking, file I/O, user interaction).  
- Background tasks that run concurrently.  

---

## 2. Creating a Thread
The Thread object us is similar to Process but has the advantage of
 - global accessible memory safe variable

Threading workflow also does not require the ```__name__ == "__main__"``` condition to execute 
```python
import threading
import time

def worker(name):
    print(f"Thread {name} starting")
    time.sleep(2)
    print(f"Thread {name} finished")

t1 = threading.Thread(target=worker, args=("A",))
t2 = threading.Thread(target=worker, args=("B",))
t1.start()
t2.start()
t1.join()
t2.join()
print("Both threads finished")
```

---

## 3. Using Locks
Threads share memory, so use locks to avoid race conditions.
```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:   # Lock acquired, prevents race conditions
            counter += 1

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print("Final counter:", counter)
```

---

## 4. Reentrant Locks (RLock)
`RLock` allows the same thread to acquire the lock multiple times safely.
```python
import threading

lock = threading.RLock()

def task():
    with lock:
        print("Outer lock acquired")
        with lock:  # same thread acquires again
            print("Inner lock acquired")

threading.Thread(target=task).start()
```

---

## 5. Semaphores
Semaphores control access to a resource pool with a set number of slots.
```python
import threading, time

sem = threading.Semaphore(2)  # max 2 threads allowed at once

def worker(i):
    with sem:
        print(f"Thread {i} entered")
        time.sleep(2)
        print(f"Thread {i} exiting")

for i in range(5):
    threading.Thread(target=worker, args=(i,)).start()
```

---

## 6. Events
`Event` is a signaling mechanism between threads.
```python
import threading, time

event = threading.Event()

def waiter():
    print("Waiting for event to be set...")
    event.wait()
    print("Event detected, continuing")

def setter():
    time.sleep(2)
    print("Setting event")
    event.set()

threading.Thread(target=waiter).start()
threading.Thread(target=setter).start()
```

---

## 7. Conditions
`Condition` lets threads wait for certain states and notifies them when ready.
```python
import threading, time

condition = threading.Condition()
items = []

def producer():
    for i in range(3):
        time.sleep(1)
        with condition:
            items.append(i)
            print("Produced:", i)
            condition.notify()

def consumer():
    for _ in range(3):
        with condition:
            condition.wait()  # waits until notified
            print("Consumed:", items.pop(0))

threading.Thread(target=consumer).start()
threading.Thread(target=producer).start()
```

---

## 8. Daemon Threads
A daemon thread runs in the background and exits when the main program exits.
```python
import threading, time

def background():
    while True:
        print("Background thread running")
        time.sleep(1)

t = threading.Thread(target=background, daemon=True)
t.start()

time.sleep(3)
print("Main program exiting")
```

---

## 9. Conclusion
The `threading` module is great for I/O-bound tasks but does not provide true parallelism due to the GIL.  
It offers a range of synchronization primitives to coordinate threads safely:
- **Lock / RLock** → Prevent race conditions.  
- **Semaphore** → Limit concurrent access to resources.  
- **Event** → Signal between threads.  
- **Condition** → Wait for specific states before proceeding.  

---

## 10. References
- Python Docs: [threading](https://docs.python.org/3/library/threading.html)  
- Real Python: [Python Threading](https://realpython.com/intro-to-python-threading/)  
- Medium: [Semaphores, and Barriers](https://medium.com/@jaklimoff/python-threading-semaphores-and-barriers-e7ff65aa79ad)  
