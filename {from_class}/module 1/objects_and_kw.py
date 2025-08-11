# everything in python is an object or keyword
#print este obiect in python
from operator import truediv
#type este functie build in
#objects
print(print)
print(print.__name__)

#acest string este tot un obiect

print('Hello Python {}'.format('value'))

#toate keyword urile apar cu galben
#un keyword poate fi si obiect cat si keyword

#keywords
pass
True
False

#types
var1=-1
var2='1'
print(type(var1))
print(type(var2))

#methods
#numerele au lungime dinamica

print(var1.bit_length()) #pe cati biti este scris numarul nostru
#print(1.bit_length()) #eroare de sintaxa, caci asa sunt scrise si nr cu virgula
print((1).bit_length())
print("-----------------------")

#operations

print("1"+"1") #pt string + face concatenare
# print(1+2)pt int uri face adunare
#print((1).__add__(2))
print("1".__add__("2"))
#exista metode pentru fiecare operatie pe care o facem
#alte operatii scadere, inmultire
#exponentiere
print(2 ** 1 ** 4)
print((3).__pow__(2))
print(3//2) #returneaza int si restu e separat
print(10/3)#rezultatul ar fi cu perioada , exista functii separate in python
#impartirea da mereu float
print(type(10/2))
print("----------------")

print(2 * "3")#operatie de multiplicare , afiseaza "3" de 2 ori
#print(3 + "2") restul operatiilor nu se pot face

#string cu bool
print(True*"2")
print("-------------------------")
#DE STUDIAT ASTEA
print(True and False)
print('a' and 'b')
#prima conditie dicteaza rezultatul
#print('' and 'b')
#and nu se uita la obiecte si ia doar varianta lor de adevar
#o sa aplice : daca a e adevarat, valoarea lui b va dicta ce se returneaza
#aceeasi logica si pt OR