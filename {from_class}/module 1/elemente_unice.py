my_list = [1, 2, 4, 4, 1, 4, 2, 6, 2, 9]
unique_list = []

for item in my_list:
    if item not in unique_list:
        unique_list.append(item)

print("The list with unique elements only:")
print(unique_list)
