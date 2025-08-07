print("Salut", "New modul", sep='#', end='\t')
print('\n')
# Data type string

string1 = 'Helau1'
string2 = u"Helau2\n"
string3 = '''
Helau3
'''
string4 = """
Helau4
"""
string5 = r'Helau5 \n' # this will ignore the escape sequence
string6 = f'Helau6\n{string1}' # formated string - varianta des folosita

print(string2)
print(string5)
print(string6)

def x():
    """doc string - este luat ca un comment"""
    x = 3
    """string normal - nu este luat ca un comment"""
    """dosc string-ul poate fi doar la inceputul functiei"""