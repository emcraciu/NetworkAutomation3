var1 = 0
while var1 < 5:
    print(var1)

    var1 += 1


print('*'* 80)
while var1 < 5:
    var1 += 1
    if var1 % 2 == 0:
        continue
    print(var1)

print('*'* 80)
var1 = 1
while var1 < 5:
    var1 += 1
    if var1 % 4 == 0:
        break
    print(var1)

print('*' * 80)
var1 = 1
while var1 < 5:
    var1 += 1
    if var1 % 4 == 0:
        # continue
        break
    print(var1)
else:
    print('loop finished')