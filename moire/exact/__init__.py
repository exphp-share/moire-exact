
from moire.util import public

__all__ = '''
	MoirePattern
	is_squarefree
	find_nicer_cell
'''.split()

from .pattern import MoirePattern
from .util import is_squarefree

# Aesthetically speaking, cells where the two diagonals (geometrically speaking)
# have similar length look nicer.
def find_nicer_cell(mat):
	from sympy import Matrix
	from moire.util import window2, iterate
	MAX_MULT = 2
	def neighborhood(mat):
		for i,j in [(0,1), (1,0)]:
			# deliberately produces at least one copy of mat itself
			#  in case we're at the fixed point
			for mult in range(-MAX_MULT, MAX_MULT+1):
				m = Matrix(mat)
				m.zip_row_op(i,j, lambda a,b: a+mult*b)
				yield m

	# Ugliness is proportional to square sum of diagonal lengths;
	# (u+v).(u+v) + (u-v).(u-v)  ~  u.u + v.v
	ugliness      = lambda m: sum(x**2 for x in m)
	best_neighbor = lambda m: min(neighborhood(m), key=ugliness)

	for (old,new) in window2(iterate(best_neighbor, mat)):
		if ugliness(old) <= ugliness(new):
			return old
	assert False, 'unreachable'

# yer all public
from .constants import * # noqa
from .constants import __all__ as tmp
__all__ += tmp
