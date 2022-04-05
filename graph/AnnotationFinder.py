from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from matplotlib.pyplot import gca


class AnnotationFinder(QWidget):
	"""
	callback for matplotlib to visit a node (display an annotation) when points are clicked on.  The
	point which is closest to the click and within x_tolerance and y_tolerance is identified.
	"""

	_annotation_update = pyqtSignal(str)

	def __init__(self, xdata, ydata, annotations, axis=None, x_tolerance=None, y_tolerance=None):

		super().__init__()

		self.data = list(zip(xdata, ydata, annotations))
		if x_tolerance is None:
			x_tolerance = ((max(xdata) - min(xdata)) / float(len(xdata))) / 2
		if y_tolerance is None:
			y_tolerance = ((max(ydata) - min(ydata)) / float(len(ydata))) / 2
		self.x_tolerance = x_tolerance
		self.y_tolerance = y_tolerance
		if axis is None:
			axis = gca()
		self.axis = axis
		self.drawnAnnotations = {}
		self.links = []

	def __call__(self, event):
		if event.inaxes:
			click_x = event.xdata
			click_y = event.ydata
			if self.axis is None or self.axis == event.inaxes:
				annotations = []
				smallest_x_dist = float('inf')
				smallest_y_dist = float('inf')

				for x, y, a in self.data:
					if abs(click_x - x) <= smallest_x_dist and abs(click_y - y) <= smallest_y_dist:
						dx, dy = x - click_x, y - click_y
						annotations.append((dx * dx + dy * dy, x, y, a))
						smallest_x_dist = abs(click_x - x)
						smallest_y_dist = abs(click_y - y)
				if annotations:
					annotations.sort()  # to select the nearest node
					self._annotation_update.emit(annotations[0][-1])
					distance, x, y, annotations = annotations[0]
					# self.draw_annotation(event.inaxes, x, y, annotations)

	def get_annotation_update_signal(self):
		return self._annotation_update

	def draw_annotation(self, axis, x, y, annotation):
		if (x, y) in self.drawnAnnotations:
			markers = self.drawnAnnotations[(x, y)]
			for m in markers:
				m.set_visible(not m.get_visible())
			self.axis.figure.canvas.draw()
		else:
			t = axis.text(x, y, "%s" % annotation, )
			m = axis.scatter([x], [y], marker='d', c='r', zorder=100)
			self.drawnAnnotations[(x, y)] = (t, m)
			self.axis.figure.canvas.draw()
