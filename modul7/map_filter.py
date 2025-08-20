# map function
list_to_map = [0,1,2,3]
result = map(lambda x: x + 1, list_to_map)

list_to_map.append(4) # since result is not iterated the changes to list_to_map will be processed

print(type(result))

for element in result:
    print(element)

print(list(result)) # iterator is already consumed

# filter function

list_to_filter = [0,1,2,3]
result = filter(lambda x: x - 1, list_to_filter)

print(type(result))

list_to_filter.append(4)  # since result is not iterated the changes to list_to_filter will be processed

for element in result:
    print(element)

