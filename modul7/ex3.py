# create list of functions where function is x + Y and Y is incremented from 1 to 100

list_of_func = []
for number in range(1, 101):
    func = lambda x : x + number # fix variable change in function !!
    # func = lambda x, y=number: x + y  # Alexandra (1p)
    list_of_func.append(func)

print(list_of_func)

print(list_of_func[0](2))
print(list_of_func[1](2))