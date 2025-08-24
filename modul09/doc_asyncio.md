# Module9: Asynchronous Execution in Python

## 1. Introduction
Asynchronous execution allows Python programs to perform multiple tasks concurrently without blocking the main execution thread.  
This is especially useful when working with tasks that involve **I/O operations** (e.g., reading/writing files, network requests, database queries).  

Key benefits:
- Efficient handling of many I/O-bound operations.  
- Improved program responsiveness.  
- Ability to scale without threads or processes in many cases.  

---

## 2. The `asyncio` Module
Python’s built-in `asyncio` module provides the foundation for asynchronous programming. It introduces two main concepts:
- **Coroutines** (declared with `async def`).  
- **The event loop** (manages scheduling and execution of coroutines).  

Example: A simple coroutine
```python
import asyncio

async def greet():
    print("Hello...")
    await asyncio.sleep(1)
    print("...World!")

asyncio.run(greet())
```

**Explanation**:  
- `async def` defines a coroutine.  
- `await asyncio.sleep(1)` suspends execution for 1 second without blocking the entire program.
- `asyncio.run` creates an event loop that will loop over awaited statements and terminate the loop on return

---

## 3. Running Multiple Coroutines
You can run multiple coroutines concurrently using `asyncio.gather`.

```python
import asyncio

async def task(name, delay):
    await asyncio.sleep(delay)
    print(f"Task {name} finished after {delay} seconds")

async def main():
    await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3)
    )

asyncio.run(main())
```

**Explanation**:  
 - all three tasks run concurrently, and their outputs appear as soon as each task finishes.
 - `asyncio.gather` creates a single event loop with all awaited statements from all tasks 

---

## 4. Asynchronous I/O Example
A real-world use case is fetching multiple URLs simultaneously.

```python
import asyncio
import aiohttp

async def fetch(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/3",
        "https://httpbin.org/delay/1"
    ]
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(fetch(session, url) for url in urls))
        for i, result in enumerate(results, 1):
            print(f"Response {i} length: {len(result)}")

asyncio.run(main())
```

**Explanation**:  
- Instead of waiting for each request sequentially, all requests are made concurrently.  
- This drastically reduces overall execution time compared to synchronous code.  

---

## 5. When to Use Asynchronous Execution
- Network requests (web scraping, APIs).  
- Database queries with async drivers.  
- Handling multiple socket connections (e.g., chat servers).  

Not recommended for:
- CPU-bound tasks (use multiprocessing or threading instead).  

---

## 6. Conclusion
Asynchronous execution makes Python programs more efficient and scalable when handling I/O-bound tasks. By leveraging `asyncio` and async libraries like `aiohttp`, developers can write high-performance concurrent code without complex thread management.  

---

## 7. References
- Python official documentation: [asyncio](https://docs.python.org/3/library/asyncio.html)  
- Real Python: [Async IO in Python](https://realpython.com/async-io-python/)  
- Aiohttp documentation: [aiohttp](https://docs.aiohttp.org/en/stable/)  
