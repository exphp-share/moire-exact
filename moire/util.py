
import functools
import sys

# hello copy-pasta:

def public(f):
	""" Use a decorator to avoid retyping function/class names.

	* Based on an idea by Duncan Booth:
	  http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
	* Improved via a suggestion by Dave Angel:
	  http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1
	"""
	all = sys.modules[f.__module__].__dict__.setdefault('__all__', [])
	if f.__name__ not in all:  # Prevent duplicates if run from an IDE.
		all.append(f.__name__)
	return f
public(public)  # Emulate decorating ourself

@public
class as_container:
	'''
	Decorator to automatically thread the output of a function through another.
	It is primarily used to allow a function written using generator syntax
	to return a fully evaluated sequence.
	'''
	def __init__(self, klass):
		self.klass = klass
	def __call__(self, func):
		return functools.wraps(func)(lambda *a,**kw: self.klass(func(*a,**kw)))

@public
def dict_update(d1, d2, **kw):
	'''
	Functional style dict.update (i.e. has a return value,
	and the original dicts are not modified)
	'''
	d = dict(d1)
	d.update(d2, **kw)
	return d

@public
def unpack_dict(d, *keys):
	''' A checked deconstruction of all keys in a dict. '''
	d = dict(d)
	for k in keys: yield d.pop(k)
	for k in d: raise KeyError('unpack_dict: Unrecognized key: {!r}'.format(k))

@public
def iterate(function, start):
	''' Functional iteration.  Yields x, f(x), f(f(x)), f(f(f(x)))... '''
	while True:
		yield start
		start = function(start)

@public
def flatten(iterable):
	''' Remove one level of nesting from nested iterables. '''
	for x in iterable:
		for y in x:
			yield y

@public
def window2(iterable):
	'''
	Overlapping pairs.

	[a,b,c,d,...] --> [(a,b), (b,c), (c,d), ...]
	'''
	it = iter(iterable)
	prev = next(it)
	for x in it:
		yield prev, x
		prev = x

@public
def strict_zip(*iterables):
	'''
	A non-lazy zip which checks that lengths are equal.
	'''
	lists = [list(x) for x in iterables]
	if count_unique(map(len, lists)) > 1:
		raise ValueError('strict_zip: iterables of different length')
	return zip(*lists)

@public
def count_unique(iterable):
	''' get number of unique items in an iterable. (items must be hashable) '''
	return len(set(iterable))

@public
def compose_random(*tups):
	''' [(weight, func, *args)] -> picks from weighted sum of random distributions '''
	import numpy as np
	# choose which distribution to use by weighted choice
	weights = np.array([w[0] for w in tups])
	weights = weights / np.sum(weights)
	index = np.random.choice(range(len(tups)), p=weights)

	# generate from that distribution
	func = tups[index][1]
	args = tups[index][2:]
	return func(*args)
