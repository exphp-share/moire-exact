
from sympy import S, Symbol
from sympy import ImmutableMatrix, Tuple
from sympy import gcd, sqrt
from sympy import simplify

import itertools

from .pattern import MoirePattern
from .util import undummy, is_squarefree
from moire.util import public

__doc__ = ''' Moire-pattern-constructing primitives '''

# most of these methods can take either symbolic or numerical arguments.
# Many of them perform additional validation when given numerical arguments.
@public
def rotation_cart(*, sine=S('s'), cosine=S('t')):
	(sine,cosine) = map(S, (sine,cosine))
	if not any(x.free_symbols for x in (sine,cosine)):
		assert sine*sine + cosine*cosine == 1
	return ImmutableMatrix([[cosine,-sine],[sine,cosine]])

@public
def reflection_cart(*, sine=S('s'), cosine=S('t')):
	(sine,cosine) = map(S, (sine,cosine))
	if not any(x.free_symbols for x in (sine,cosine)):
		assert sine*sine + cosine*cosine == 1
	return ImmutableMatrix([[cosine,sine],[sine,-cosine]])

# NOTE: These are all horribly documented, and basically you need to read
#       my moire paper.

@public
def prim_rotation_moire_abc(*, β=Symbol('β'), a=S('a'), b=S('b'), c=S('c')):
	(a,b,c,β) = map(S, (a,b,c,β))
	if not any(x.free_symbols for x in (a,b,c,β)):
		assert gcd(a,b*β) == gcd(a,c) == 1
		assert a*a + β*b*b == c*c
	amat = prim_rotation_cell(β)
	mmat = rotation_cart(sine=b*sqrt(β)/c, cosine=a/c)
	if not mmat.free_symbols:
		assert mmat.det() == 1
	return MoirePattern.from_opers(amat, cart=mmat)

@public
def prim_scaled_rotation_moire_abck(*, β=Symbol('β'), a=S('a'), b=S('b'), c=S('c'), k=S('k')):
	# FIXME this is currently mostly a copy-paste of prim_rotation_moire_abc
	#  which differs in no discernable way except assertions, which are
	#  only slightly more general.  Once I am certain that this is correct,
	#  prim_rotation_moire_abc should simply delegate to this with k==1.
	(a,b,c,k,β) = map(S, (a,b,c,k,β))
	if not any(x.free_symbols for x in (a,b,c,k,β)):
		assert gcd(a,b*β) == gcd(a,k*c) == 1
		assert a*a + β*b*b == c*c
	amat = prim_rotation_cell(β)
	mmat = rotation_cart(sine=b*sqrt(β)/c, cosine=a/c)
	if not mmat.free_symbols:
		assert mmat.det() == k
	return MoirePattern.from_opers(amat, cart=mmat)

@public
def prim_rotation_moire_pq(*, β, p=S('p'), q=S('q')):
	(p,q,β) = map(S, (p,q,β))
	if not any(x.free_symbols for x in (p,q,β)):
		assert gcd(p,q) == 1
	(a,b,c) = rotation_diophantine_triple(β, p=p, q=q)
	return prim_rotation_moire_abc(β=β, a=a, b=b, c=c)

@public
def prim_special_reflection_moire(*, t=S('t')):
	t = S(t)
	amat = prim_special_reflection_cell(cosine=t)
	mmat = reflection_cart(cosine=t, sine=sqrt(1-t**2))
	return MoirePattern.from_opers(amat, cart=mmat)

# FIXME:
# This smells fishy.
# The parametrization returned for x*x + 3*y*y - z*z == 0 is does not
#  appear to be capable of producing the result (x,y,z) == (11, 5, 14)?
#
# I looked at the cited source, and on page 55 he "[multiplies] p and q
# by their common denominator so that they take coprime values." I am unable
# to come up with any valid interpretation of this sentence or definition of
# his variable "g" that results in anything like Eq. (IV.2)
#
# Resource:
# The algorithmic resolution of Diophantine equations,
#   Nigel P. Smart, London Mathematical Society Student Texts 41,
#   Cambridge University Press, Cambridge, 1998.
# Provided by sympy
@public
def rotation_diophantine_triple(β, p=S('p'), q=S('q')):
	from sympy.solvers.diophantine import parametrize_ternary_quadratic
	from sympy import Dummy
	x,y,z = map(Dummy, 'x y z'.split(' '))
	sol = parametrize_ternary_quadratic(x*x + β*y*y - z*z)
	sol = Tuple(*undummy(sol)) # replace dummy p and q
	sol = sol.subs({S('p'): p, S('q'): q})

	# conditions on p and q are not entirely clear;  beta=3, p=1, q=1
	#  for instance gives a non-coprime solution 2 2 4
	(a,b,c) = sol
	if not sol.free_symbols:
		assert gcd(a,β*b) == gcd(c,β*b) == gcd(a,c) == 1

	# ...there doesn't seem to be a way to tell parametrize_ternary_quadratic
	#  what order my variables are in. It literally just... *guesses*.
	for (a,b,c) in itertools.permutations(sol):
		if simplify(a*a + β*b*b - c*c) == 0:
			return Tuple(a,b,c)
	assert False, 'huh, we really expected one of those to work'

@public
def prim_rotation_cell(β):
	'''
	Representative family member of cells of the form [[1,0],[x,y]]
	where x and y*y are rational.
	'''
	β = S(β)
	if not β.free_symbols:
		assert is_squarefree(β)
	return ImmutableMatrix([[1,0], [0,sqrt(β)]])

@public
def prim_special_reflection_cell(cosine):
	'''
	Representative family member of cells of the form [[1,0],[x,y]]
	that support a reflection with an irrational cosine.
	'''
	cosine = S(cosine)
	return ImmutableMatrix([[1,0], [cosine, sqrt(1-cosine*cosine)]])

