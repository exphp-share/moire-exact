import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models import ColumnDataSource, Slider, TextInput
from bokeh.plotting import figure
from bokeh.models import Range1d
from itertools import starmap


def main():
	zoom = 4
	index_radius = [30,30]

	# set up plot (styling in theme.yaml)
	plot = figure(toolbar_location=None, title='test', plot_width=600, plot_height=600)
	source1 = ColumnDataSource(data=dict(x=[], y=[]))
	source2 = ColumnDataSource(data=dict(x=[], y=[]))
	plot.circle('x', 'y', source=source2, size=5, color='black')
	plot.circle('x', 'y', source=source1, size=10)

	scale_slider = Slider(
		title="Scale", value=0.018,
		start=0.0, end=3.0, step=0.0001,
		width=400)
	rotation_slider = Slider(
		title="Rotation", value=10.8,
		start=0.0, end=60.0, step=0.0001,
		width=400)
	translation_slider = Slider(
		title="Translation", value=0.5,
		start=0.0, end=0.5, step=0.0001,
		width=400)

	center_i_input = TextInput(title="Viewpoint Center I", value="0")
	center_j_input = TextInput(title="Viewpoint Center J", value="0")

	# filler values; this is only to ensure that they are instances of Range1d.
	plot.x_range = Range1d(0,1)
	plot.y_range = Range1d(0,1)

	# that does it.
	# I'm just going to write one big miserable mess of a function
	# so terrible that my OCPD will be incapable of "fixing" it
	def update():
		try:
			direct_center = [float(center_i_input.value), float(center_j_input.value)]
		except ValueError:
			direct_center = [0., 0.]


		HEX_CELL = np.array([[1, 0], [0.5, 3**0.5/2]])
		def rotation_matrix(theta):
			s,c = np.sin(theta), np.cos(theta)
			return np.array([[c,-s],[s,c]])
		def get_cell(cell, rotation=0, scale=1):
			return cell.dot(rotation_matrix(rotation).transpose())*scale

		def cart_data(i, j, cell):
			ijs = np.column_stack([i, j])
			xys = ijs.dot(cell)
			x,y = xys.transpose()
			return dict(x=x, y=y)

		from math import radians
		cell1 = get_cell(HEX_CELL)
		cell2 = get_cell(HEX_CELL,
			rotation=radians(rotation_slider.value),
			scale=(1 + scale_slider.value),
		)

		# recenter plot
		# update range start and end in-place
		#  to work around this: https://github.com/bokeh/bokeh/issues/4014
		[cart_center] = np.array([direct_center]).dot(cell1)
		plot.x_range.start = cart_center[0] - 4.*zoom
		plot.x_range.end   = cart_center[0] + 4.*zoom
		plot.y_range.start = cart_center[1] - 4.*zoom
		plot.y_range.end   = cart_center[1] + 4.*zoom

		def nearest_index(cell, cart):
			direct = np.array([cart]).dot(np.linalg.inv(cell))
			# note: numpy floats do not round to ints like python floats do
			return [int(round(x)) for x in direct.flat]

		def direct_coords(cell, cart_center):
			index_center = nearest_index(cell, cart_center)
			assert all(isinstance(x, int) for x in index_center)
			def index_span(center, radius):
				return np.arange(center-radius, center+radius+1)
			I,J = starmap(index_span, zip(index_center, index_radius))
			i,j = [x.reshape(-1) for x in np.meshgrid(I, J)]
			return i,j

		i1,j1 = direct_coords(cell1, cart_center)
		i2,j2 = direct_coords(cell2, cart_center)
		source1.data = cart_data(i1,                            j1, cell1)
		source2.data = cart_data(i2 + translation_slider.value, j2, cell2)


	def callback(i, dont, care):
		update()

	update() # initialize
	scale_slider.on_change('value', callback)
	rotation_slider.on_change('value', callback)
	translation_slider.on_change('value', callback)
	print(dir(plot))

	# set up layout
	center_i_input.on_change('value', callback)
	center_j_input.on_change('value', callback)
	inputs = column(widgetbox(
		scale_slider,
		rotation_slider,
		translation_slider),
		row(center_i_input, center_j_input),
	)

	# add to document
	curdoc().add_root(row(inputs, plot))
	curdoc().title = "Clustering"


main()
