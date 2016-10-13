
# this module exists because HRRRNG circular dependencies
__all__ = '''
	SYMP_EYE
	SYMP_ZERO
	HEX_β
	HEX_INDEX
'''.split()

from sympy import S
from sympy import ImmutableMatrix

SYMP_EYE  = ImmutableMatrix([[1,0],[0,1]]) # nyeah
SYMP_ZERO = ImmutableMatrix([[0,0],[0,0]])

HEX_β = 3
HEX_INDEX = ImmutableMatrix(S('[[1,0],[1/2,1/2]]'))
