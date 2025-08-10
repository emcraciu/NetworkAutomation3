#poate primi oricate argumente
#astea sunt by default sep=" " si end='\n'
print('Hello Python',"New Module ", sep='%',end='\t')

#data type string
#u by default , u sau nimic inseamna acelasi lucru, unicode
string1= u'Hello Python1'
print(string1)
string2="\nHello Python2\n"
print(string2)
string3= '''
Hello Python3
'''
string4= """Hello Python4""" #astea sunt si multiline
print(string4)

#this will ignore the escape sequence
string5= r'Hello Python5\n' #\n nu l mai ia ca si caracter special, la fel si pe toate celelalte
print(string5)

#o variabila este formatata in interiorul sting ului nostru
string6= f'Hello Python6\n{string1}' #formated string

print(string6)

#Pentru string-uri putem pune in fata u care nu afecteaza cu absolut nimic
#putem  pune r care inseamna ca anuleaza efectul caracterrelor speciale precum \n
#putem pune f pentru s scrie un string in interiorul unui alt string
