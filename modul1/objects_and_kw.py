# everything in python is an object or keyword

# objects
print(print)

print(print.__name__)

'Hello Python {}'.format('value')

#keywords
pass
True
False

var1=1
var2 ='1'

print(type(var1))
print(type(var2))

# methods
print(var1.bit_length())
print((1).bit_length())

# operations
print(1+2)
print((1).__add__(2))
print("1"+"2")
print("1".__add__("2"))

print(3 ** 2)
print((3).__pow__(2))

print(10/3) #not exact
print(type(10/3))

print(10//3)
print(type(10//3))
print(3//2)
print(4//2)
print((4).__floordiv__(2))

print(2*"2")
print(False*"2")

print(True and False)
print('a' and 'b')
