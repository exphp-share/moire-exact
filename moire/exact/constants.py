# encoding: utf-8
from __future__ import unicode_literals

# this module exists because HRRRNG circular dependencies
__all__ = [
	'SYMP_EYE',
	'SYMP_ZERO',
	'HEX_BETA',
	'HEX_INDEX',
]


from sympy import S
from sympy import ImmutableMatrix

SYMP_EYE  = ImmutableMatrix([[1,0],[0,1]]) # nyeah
SYMP_ZERO = ImmutableMatrix([[0,0],[0,0]])

HEX_BETA  = 3
HEX_INDEX = ImmutableMatrix(S('[[1,0],[1/2,1/2]]'))

# tsk tsk tsk python 2
import sys
if sys.version_info[0] >= 3:
	globals()['HEX_β'] = HEX_BETA
	__all__.append('HEX_β')
