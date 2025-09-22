import pylint
import sys
print(sys.path)


args = [ '--rcfile=pylintrc', 'modul16/configure_ftd_int.py']
pylint.run_pylint(args)