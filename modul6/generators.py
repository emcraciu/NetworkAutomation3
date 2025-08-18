# range generator

print(type(range(1,11)))
print(type(range))


def my_range(start, stop):
    i = start
    while i <= stop:
        yield i
        i += 1
        if i == 4:
            return

gen = my_range(1,11)
print(gen)
print(next(gen))
print(next(gen))
print(next(gen))
try:
    print(next(gen))
except StopIteration:
    print(next(gen))