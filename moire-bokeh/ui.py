from bokeh.models import Slider, TextInput
from bokeh.layouts import row, column

import math

class SliderTextInputPair:
	def __init__(self, type, value, width=None, title=None, **slider_kw):
		self._type = type

		input_kw = {}
		if title is not None:
			input_kw['title'] = title
			slider_kw['title'] = title
		if width is not None:
			raise ValueError('width cannot be set, things are broken')

		self._slider = Slider(
			value=value,
			# HACK: try to limit buildup of callbacks to some degree
			callback_policy='throttle', callback_throttle=int(1/5 * 10**6),
			**slider_kw)

		self._input = TextInput(
			value=str(value),
			**input_kw)

		self.value = value
		self.model = row(self._slider, self._input)

	def _slider_cb(self, attr, old, new):
		self.value = new
		self._set_input_value(self.value)
		self._callback(attr, old, new)

	def _input_cb(self, attr, old, new):
		try: self.value = self._type(new)
		except ValueError: return
		self._set_slider_value(self.value)
		self._callback(attr, old, new)

	def _set_slider_value(self, value):
		# NOTE: This assumes bound methods for the same instance always
		#       have the same id; I don't know if this is guaranteed.
		self._slider.remove_on_change('value', self._slider_cb)
		self._slider.value = value
		self._slider.on_change('value', self._slider_cb)

	def _set_input_value(self, value):
		self._input.remove_on_change('value', self._input_cb)
		self._input.value = str(value)
		self._input.on_change('value', self._input_cb)

	def add_callback(self, callback):
		self._callback = callback
		self._slider.on_change('value', self._slider_cb)
		self._input.on_change('value', self._input_cb)

class ShapeSelect:

	def __init__(self, **kw):

		self._rotation = SliderTextInputPair(
			title="Angle α",
			type=float_eval, value=90,
			start=1e-3, end=180-1e-3, step=1e-3,
			)

		self._ratio = SliderTextInputPair(
			title="Ratio b/a",
			type=float_eval, value=1.0,
			start=0.25, end=4.0, step=0.01,
			)

		self.model = column(
			self._rotation.model,
			self._ratio.model,
		)

	def cell(self):
		def row(rotation, magnitude):
			return [f(rotation) * magnitude for f in (math.cos, math.sin)]
		return [row(*a) for a in zip(self.rotations(), self.magnitudes())]

	def rotations(self):  return (0, math.radians(self._rotation.value))
	def magnitudes(self): return (1, self._ratio.value)

	def add_callback(self, callback):
		self._rotation.add_callback(callback)
		self._ratio.add_callback(callback)



def float_eval(s):
	# NOTE: by no means is this intended to be secure
	badchars = set(s) - set(' \t1234567890.eE-+*/()')
	if badchars:
		raise ValueError
	return float(eval(s))
