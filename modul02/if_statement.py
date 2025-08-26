var1 = int(input("Enter a number: "))
if 3 > var1:
    print(f"3 is greater than {var1}")
elif var1 < 3:
    print(f"3 is less than {var1}")
elif var1 < 2:
    print(f"2 is less than {var1}") # will never be executed
else:
    print(f"3 is not greater than {var1}")

