import telnetlib3
import sys
# from modul4.example_import import example_var, example_func1
# from example_package import package_variable1, example_func2
# from example_package import *
# from modul4.example_import import *

# print(example_var)
# print(package_variable1)
# example_func1()
# example_func2()
# print(i)

from modul4.example_import import example_var, example_func1
import example_package as ep

print(ep)
ep.example_func2()

print(sys.path)
