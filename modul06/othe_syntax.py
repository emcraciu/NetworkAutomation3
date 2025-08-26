# list comprehencion

odd = [var for var in range(100) if var % 2]
print(odd)

odd = {var: var +1 for var in range(100) if var % 2}
print(odd)

even = (var for var in range(100) if not var % 2)

print(even)
print("First Number",next(even))
for nr in even:
    print(nr)

# print(list('test'))