# function as object
from math import prod

def generic_function(message: str):
    return str(f'generic function: {message}')

def add_function(message: str):
    sum_ = 0
    try:
        l = message.split(",")
        for item in l:
            sum_ += int(item)
    except:
        print("Something went wrong")
    return sum_

def multiple_functions(message: str):
    operands = message.split(',')
    operands_v2: list[int] = []
    for index, number in enumerate(operands):
        operands[index] = int(number)
    return prod(operands_v2)

list_of_functions = [
    lambda message: str(f'generic function: {message}'),
    add_function,
    multiple_functions,
]

dict_of_functions = {
    '*': multiple_functions,
    '+': add_function,
    '_': lambda message: str(f'generic function: {message}'),
}

# print([list_of_functions])
user_message = input('Enter your message: ')
user_function = input('Enter your function: ')

for f in list_of_functions:
    if user_function in f.__name__:
        found_function = f
        print('found function:', found_function.__name__)
try:
    found_function
except NameError:
    for key, f in dict_of_functions.items():
        if key == user_function:
            found_function = f


print(found_function(user_message))