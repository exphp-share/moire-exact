from sympy import simplify
from sympy import ImmutableMatrix, Matrix
from sympy import lcm

import itertools

from .constants import SYMP_EYE, SYMP_ZERO
from moire.util import public

@public
class MoirePattern:
	'''
	Describes a Moire pattern produced by two cells A and B.

	A MoirePattern may have free variables;
	However, once there are no free variables in E,
	 a commensurate supercell can be obtained.
	'''
	def __init__(self, *, dont_use):
		''' Do not initialize directly. Please use the named constructors instead. '''
		pass

	@classmethod
	def from_cells(klass, a, b):
		''' Construct from two cell matrices (A and B). '''
		return klass.from_abe(a, b, b*a.inv())

	@classmethod
	def from_opers(klass, a1, *, a2=None, scale=1, rows=SYMP_EYE, cart=SYMP_EYE):
		'''
		Construct from one cell matrix A and two transformations.

		The second cell matrix is produced by applying one transformation to
		each side;  B = M1 * A * M2^T.  Effectively, M1 takes a linear combination
		of the rows, while M2 operates on each row as a cartesian vector.
		'''
		return klass.from_cells(a1, scale * rows * (a2 or a1) * cart.T)

	@classmethod
	def from_abe(klass, a, b, e, *, c=None):
		'''
		Primary constructor.

		Takes both cells A and B and the rational matrix  E = B A^-1.
		Its raison d'etre is to allow E to be parametrized in terms of more
		meaningful variables. It also validates the relation between A, B, and E,
		and computes the supercell matrix once enough variables have been substituted.
		'''
		self = klass(dont_use=0)
		assert simplify(e * a - b) == SYMP_ZERO, "{} \n VERSUS \n {}".format(e*a, b)
		(self._a, self._b, self._e) = (ImmutableMatrix(simplify(x)) for x in (a,b,e))
		self._c = c

		if self._c is None and not self._e.free_symbols:
			assert all(x.is_rational for x in self._e), str(self._e)
			self._c = self._bruteforce_c(e)
		return self

	@staticmethod
	def _bruteforce_c(e):
		'''
		Locate HNF matrix C such that C * E^-1 is integral
		in a slightly dumb manner.
		'''
		e = e.inv()
		is_row_ok = lambda row: all(x.is_integer for x in row * e)
		denominator = lambda rat: rat.as_numer_denom()[1]

		# First element is easy enough...
		c00 = lcm(denominator(e[0,0]), denominator(e[0,1]))
		assert is_row_ok(Matrix([[c00, 0]]))

		# Brute force the second row.
		# (note it can be done analytically with careful application
		#  of the chinese remainder theorem)
		for c11 in itertools.count(1):
			for c10 in range(c00):
				if is_row_ok(Matrix([[c10,c11]])):
					return ImmutableMatrix([[c00,0], [c10,c11]])

	def swap_cells(self):
		''' Flip the roles of A and B. '''
		# NOTE: C is thrown away and recomputed due to the
		#       invariant that we only store the HNF cell.
		return self.from_cells(self._b, self._a, self._e.inv())

	def _checked_c(self):
		if not self._c:
			raise RuntimeError(
				'E not fully evaluated yet!'
				'  Free variables: {}'.format(self._e.free_symbols))
		return self._c

	def a_matrix(self): return self._a
	def b_matrix(self): return self._b
	def e_matrix(self): return self._e
	def m_matrix(self): return (self._a.inv() * self._b).T
	def cells(self):    return (self._a, self._b)
	c_matrix = _checked_c
	c_matrix_hnf = c_matrix

	a_matrix.__doc__ = ''' The real matrix A (the primary layer's unit cell). '''
	b_matrix.__doc__ = ''' The real matrix B (the secondary layer's unit cell). '''
	e_matrix.__doc__ = ''' The rational matrix E in B = E A '''
	m_matrix.__doc__ = ''' The transformation matrix M in B = A M^T '''
	c_matrix.__doc__ = ''' The integer matrix C such that C A is the moire supercell. '''
	c_matrix_hnf.__doc__ = ''' Alias of c_matrix emphasizing the fact that C is in HNF. '''
	cells.__doc__    = ''' The two unit cells A and B. '''


	_NOT_SPECIFIED = object()
	def visit_family(self, qa, qb=_NOT_SPECIFIED):
		''' Get another moire pattern with the same cartesian transformation
		but different cells, by multiplying each cell on the left by a rational matrix.

		visit_family(self, matrix):  multiplies both cells by the same matrix.
		visit_family(self, qa, qb):  multiples each cell by a different matrix.
		                             (use None for an identity transform)
		'''
		if qb is self._NOT_SPECIFIED: qb = qa
		if qa is None: qa = SYMP_EYE
		if qb is None: qb = SYMP_EYE
		return type(self).from_abe(
			a=qa * self._a,
			b=qb * self._b,
			e=qb * self._e * qa.inv(),
			c=None, # invalidated!
		)

	def d_matrix(self):
		'''
		Get the (integer) matrix D which describes the commensurate cell
		in terms of B;  CA == BD.  This matrix is not necessarily in HNF.
		'''
		return self._e.inv() * self._checked_c()

	def d_matrix_hnf(self):
		'''
		Get the HNF form of the matrix D which describes the commensurate cell
		in terms of B.  This matrix will not satisfy  CA == BD; however, CA
		 and BD will be related by a unimodular transformation.
		'''
		return self.swap_cells().c_hnf_matrix()

	def commensurate_cell(self):
		'''
		The (real) commensurate cell matrix, which can only
		be known once no free variables remain in E
		'''
		return self._checked_c() * self._a

	def is_valid_primitive_supercell(self, mat):
		'''
		Tests if the given integer matrix can be a primitive
		supercell matrix for the moire pattern, when applied
		to A.  (i.e. is this a valid replacement for C?)
		E must be fully determined.
		'''
		mat = ImmutableMatrix(mat)
		assert all(x.is_integer for x in mat)
		# two supercell matrices are equivalent if they are related
		# by multiplication on the left by a unimodular matrix
		prod = self._checked_c() * mat.inv()
		return all(x.is_integer for x in prod) and abs(prod.det()) == 1

	def relative_supercell_volume(self):
		''' The supercell volume in units of the volume of A. '''
		v = self._checked_c().det()
		assert v.is_integer
		return v

	def subs(self, *args, **kw):
		''' Sympy symbol substitution '''
		# hack to make iterable of (var, value) reiterable:
		d = dict(*args, **kw)
		(a,b,e) = (m.subs(d) for m in (self._a, self._b, self._e))
		return type(self).from_abe(a,b,e,c=self._c)

	def __repr__(self):
		return 'MoirePattern.from_abe(\n\ta = {},\n\tb = {},\n\te = {})'.format(self._a, self._b, self._e)
