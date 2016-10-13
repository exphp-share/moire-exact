
import sympy
from sympy import sympify

from moire.util import public

@public
def undummy(expr):
	''' a terrible hack to coerce dummy variables into namable ones '''
	return sympify(str(expr))

@public
def is_squarefree(x):
	return x == sympy.ntheory.factor_.core(x)

