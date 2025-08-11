def function1(arg1, arg2, kwarg1=None, kwarg2=None):
    print(arg1, arg2, kwarg1, kwarg2)


function1('message1', "message2")
function1('message1', "message2", kwarg2='message4')
try:
    function1('message1')
except TypeError:
    print('required positional argument')


# order of arguments
# def function1(kwarg1=None, arg1, arg2, kwarg2=None):
#     print(arg1, arg2, kwarg1, kwarg2)

def function2(arg1, arg2, kwarg2=None, kwarg1=None, ):
    print(arg1, arg2, kwarg1, kwarg2)


# argument packing -
def function3(*args, argn):
    print(args, argn)


function3('message1', "message2", "message3", "message4", argn="message_n")

# *var pack unpack variables

a = 10
b = 20
a, b = b, a  # switch vars
print(a, b)

a, b, c = [1, 2, 3]
print(a, b, c)

a, *b, c = [1, 2, 3, 4, 5]
print(a, b, c)
# a, *b, *c = [1, 2, 3, 4, 5] # multiple * are not a valid syntax
# print(a, b, c)
*b, = [1, 2, 3, 4, 5]
print(b)


# argument packing -
def function4(kwarg_n=None, **kargs):
    print(kwarg_n, kargs)

function4(arg1=1, arg2=2, kwarg_n='new_value')

print(dict(keyword='value'))
print(dict(((1,2),(3,4))))

# **args = ((1,2),(3,4)) ??


# global, local, nonlocal vars
var_g = 10
print('Value of var_g:', var_g)

def function5(arg1, arg2, kwarg1=None, kwarg2=None):
    global var_g
    var_g = 15
    print('global variable from outside function:', var_g) # global variable
    print(arg1, arg2, kwarg1, kwarg2) # all local variables


function5('message1', "message2")

print('Value of var_g:', var_g)
var_non_l = 5
def fucn1():
    var_non_l = 10
    def fucn2():
        nonlocal var_non_l
        var_non_l = 20
        print('var_non_l:', var_non_l)
    fucn2()
    print('var_non_l:', var_non_l)
    return fucn2

f2 = fucn1()


# var_non_l = 5
# def fucn1():
#     var_non_l = 10
#     def fucn2():
#         print('var_non_l:', var_non_l)
#         def fucn3():
#             nonlocal var_non_l
#             var_non_l = 20
#             print('var_non_l:', var_non_l)
#     fucn2()
#     print('var_non_l:', var_non_l)
#     return fucn2

