
from __future__ import print_function

import sys

import subprocess
from setuptools import setup
from setuptools import find_packages

setup(
	name='moire',
	version = '0.1',
	description = 'Moire pattern analysis',
	url = 'https://github.com/ExpHP/this-url-wont-actually-work-because-this-isnt-uploaded-anywhere',
	author = 'Michael Lamparski',
	author_email = 'lampam@rpi.edu',

	packages=find_packages(),
	install_requires=[
		'numpy',
		'sympy',
#		'pyg', # <-- good luck with that one
#		       #     (btw, how on earth did you find THIS package?)
	],
)
