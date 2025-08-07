print('Hello Python', "new Modul", sep='%', end = '\t')

# Data Type string
string1= 'Hello Python1'
string2= "\nHello Python2\n"
print(string2)
string3= '''
Hello Python
'''
string4= """
Hello Python
"""
print(string4)
string5= r'Hello Python\n' # this will ignore the escape sequence
print(string5)
string6= f'\nHello Python\n{string1}' # formated string
print(string6)

def x():
    x = 3
    """coment"""