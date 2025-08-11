# function as object
def generic_function(message: str):
    return str(f'generic function: {message}')

def add_function(message: str):
    pass

def multiple_functions(message: str):
    pass

list_of_functions = [generic_function, add_function, multiple_functions]
print([list_of_functions])
user_message = input('Enter your message: ')
user_function = input('Enter your function: ')

for f in list_of_functions:
    if user_function in f.__name__:
        found_function = f
        print('found function:', found_function.__name__)

print(found_function(user_message))