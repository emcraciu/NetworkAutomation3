# create list of functions where function is x + Y and Y is incremented from 1 to 100
from functools import partial

list_of_func = []
for number in range(1, 101):
    func = partial(lambda x,y : x + y,y=number) # fix variable change in function !!
    # func = lambda x, y=number: x + y  # Alexandra (1p)
    list_of_func.append(func)

print(list_of_func)

print(list_of_func[0](2))#0+3=3
print(list_of_func[1](2))#1+3=4
print(list_of_func[3](2))#3+3=6 3 fiind al 3 nr din for
print(list_of_func[4](1))#4+2=6 2 fiind al doilea nr din for