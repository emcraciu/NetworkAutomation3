# everything in python is an object or keyword

# objects with methods and attributes
print(print)
print(print.__name__)
'Hello Python {}'.format('value')

# keywords
pass
True
False

# types
var1 = 3
var2 = '1'

print(type(var1))
print(type(var2))

# methods
print(var1.bit_length())
print((-1).bit_length())

# operations

print(1 + 2)
print((1).__add__(2))
print("1" + "2")
print("1".__add__("2"))

print(3 ** 2)
print((3).__pow__(2))

print(10 / 3) # not exact
print(type(10 / 2)) # returns float

print(3 * "2")
# print(3 + "2") # raises TypeError
print(True * "2")

# special cases
print(True and False)
print('' and 'b')
