for var1 in range(10):
    print(var1)

for var1 in [1, '1', None]:
    print(var1)

# == to
var1 = [1, '1', None]
var2 = var1.__iter__()
print(var2.__next__())
print(var2.__next__())
print(var2.__next__())
# print(var2.__next__()) # StopIteration causes the loop to end

# keywords for "for" loop

print(80 *"+")
for var1 in [1, 2, 3]:
    if var1 == 1:
        continue
    print(var1)

print(80 *"+")
for var1 in [1, 2, 3]:
    if var1 == 2:
        break
    print(var1)

print(80 *"+")
for continue_ in [None]:
    if continue_:
        # continue
        break
    print(continue_)
else:
    print('loop finished')
    # print('Value is: ', continue_)

print('Value is: ', continue_) # value from last iteration, value may be undefined