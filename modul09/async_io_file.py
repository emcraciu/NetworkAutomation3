# import asyncio
#
# async def greet():
#     print("Hello...")
#     await asyncio.sleep(1)
#     print("...World!")
#     await asyncio.sleep(1)
#     print("other1")
#     await asyncio.sleep(1)
#     print("other2")
#     await asyncio.sleep(1)
#     print("other3")
#
# asyncio.run(greet())

import asyncio
import time


async def task(name, delay):
    start = time.time()
    await asyncio.sleep(delay)
    print(f"Task {name} finished after {delay} seconds")
    # time.sleep(5)
    end = time.time()
    print(f"Task {name} took {end - start} seconds")

async def main():
    await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3)
    )

asyncio.run(main())