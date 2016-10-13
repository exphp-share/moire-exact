
# this module exists because HRRRNG circular dependencies
__all__ = '''
	SYMP_EYE
	SYMP_ZERO
'''.split()

from sympy import ImmutableMatrix

SYMP_EYE  = ImmutableMatrix([[1,0],[0,1]]) # nyeah
SYMP_ZERO = ImmutableMatrix([[0,0],[0,0]])
