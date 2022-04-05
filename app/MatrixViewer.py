import networkx as nx
import pandas as pd
from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from app.NaviDock import NaviTool
from app.Status import Status
from app.UserFocus import NodeFocus, UserFocus, KeywordFocus
from graph.AnnotationFinder import AnnotationFinder
from graph.MplCanvas import MplCanvas
from nlp.Algorithms import Algorithms

from pylab import *

from nlp.TextRank import TextRankWrapper


# TODO: better data sanitization and organization
class MatrixNode:

	def __init__(self, node, origin_matrix_title):
		self._type = "Matrix Node"
		self._id = node["id"]
		self._rank = node["rank"] if "rank" in node else None
		self._origin = origin_matrix_title

	def set_id(self, id_):
		self._id = id_

	def get_id(self):
		return self._id

	def get_origin(self):
		return self._origin


class KeywordEntry(MatrixNode):

	def __init__(self, node, origin_matrix_title):

		# TODO: better data sanitization
		node["keyword"] = node["id"]

		super().__init__(node, origin_matrix_title)

		self._type = "Keyword Node"
		self._keyword = node["keyword"]

	def get_keyword(self):
		return self._keyword


class SentenceEntry(MatrixNode):

	def __init__(self):
		super().__init__()


class VisualMatrix(QWidget):

	_node_select_update = pyqtSignal(MatrixNode)

	def __init__(self, nodes, edges, origin_file, matrix_title):

		super().__init__()

		self._nodes = nodes
		self._edges = edges
		self._origin_file = origin_file
		self._title = matrix_title

		self._graph = self.__build_data_graph()

	def __build_data_graph(self):

		source_ = []
		target = []
		weight = []
		for edge in self._edges:
			source_.append(edge.get_source())
			target.append(edge.get_target())
			weight.append(edge.get_weight())

		pd_edges = pd.DataFrame({'source': source_,
		                         'target': target,
		                         'weight': weight})

		nx_graph = nx.from_pandas_edgelist(pd_edges, edge_attr='weight')

		# TODO: isolate interaction layer
		pos = nx.spring_layout(nx_graph, k=0.1, iterations=20)
		x, y, annotations = [], [], []
		for key_ in pos:
			d = pos[key_]
			annotations.append(key_)
			x.append(d[0])
			y.append(d[1])

		fig = plt.figure(figsize=(10, 10))
		ax = fig.add_subplot(111)

		nx.draw(nx_graph, pos, font_size=6, node_color='#A0CBE2', edge_color='#BB0000', width=0.1,
		        node_size=2, with_labels=True)

		# TODO: isolate interaction layer
		af = AnnotationFinder(x, y, annotations)
		af.get_annotation_update_signal().connect(self.node_select)
		connect('button_press_event', af)

		return fig

	@QtCore.pyqtSlot(str)
	def node_select(self, id_):
		for n in self._nodes:
			if n.get_id() == id_:
				self._node_select_update.emit(n)

	def get_node_select_update_signal(self):
		return self._node_select_update

	def get_graph(self):
		return self._graph

	def get_nodes(self):
		return self._nodes

	def get_origin_file(self):
		return self._origin_file

	def get_title(self):
		return self._title


class KeywordMatrix(VisualMatrix):

	def __init__(self, nodes, edges, origin_file, matrix_title):
		super().__init__(nodes, edges, origin_file, matrix_title)

	def get_keywords(self):
		return [k.get_keyword() for k in self.get_nodes()]

	# TODO: better returns
	def get_keyword_entry(self, target):
		keywords = self.get_keywords()
		nodes = self.get_nodes()
		if target in keywords:
			for i in range(0, len(keywords)):
				if nodes[i].get_keyword() == target:
					return nodes[i]
			return None
		return None


class SentenceMatrix(VisualMatrix):

	def __init__(self, nodes, edges, origin_file, matrix_title):
		super().__init__(nodes, edges, origin_file, matrix_title)


class MatrixViewer(NaviTool):

	_data_update = pyqtSignal(VisualMatrix)

	def __init__(self, resolution=None):

		super().__init__("Matrix Viewer", resolution=resolution)

		self._aggregate_update = {}
		self._matrices = {}
		self._sources = []

		self._loaded_matrix = None

		# TODO: better configuration for default canvas
		self._empty_canvas_notification = QLabel("Add a File to Begin Analyzing")
		self._canvas = self._empty_canvas_notification
		self._mpl_tb = None

		super().add_inner_widget(self._canvas)

		super().get_navi_tool_bar().get_navigation_update_signal().connect(self.cycle_canvas)

	def _build_matrix(self, origin_file_title, nlp_algo):

		# TODO: better naming conventions
		# TODO: better unified id scheme
		matrix_name = origin_file_title + "_keyword_matrix"

		if nlp_algo is Algorithms.TEXTRANK:
			# TODO: better control of TextRank algo
			# TODO: better pipeline of data formatting
			tr4k = TextRankWrapper(self._file_handler.get_files()[origin_file_title])
			n = tr4k.get_node_weight()
			e_ = tr4k.get_cached_token_pairs()
			keyword_nodes = []
			keyword_edges = []
			for node in n:
				node_dict = {"id": node, "rank": n[node]}
				keyword_nodes.append(KeywordEntry(node_dict, matrix_name))
			for edge in e_:
				keyword_edges.append(KeywordEdge(edge, matrix_name))
			return KeywordMatrix(keyword_nodes, keyword_edges, origin_file_title, matrix_name)

	def add_matrix(self, matrix_title, matrix_):
		self._matrices[matrix_title] = matrix_
		self._aggregate_update[matrix_title] = matrix_.get_node_select_update_signal()
		self._aggregate_update[matrix_title].connect(self.matrix_interaction)
		super().get_navi_tool_bar().add_entry(matrix_title)

		self._data_update.emit(matrix_)

	def remove_matrix(self, matrix_title):
		self._matrices.pop(matrix_title)
		self._aggregate_update.pop(matrix_title)
		super().get_navi_tool_bar().remove_entry(matrix_title)

	def refresh(self, status):

		super().refresh(status)

		if status is Status.ADD:
			for file in super().get_file_handler().get_files():
				if file not in self._sources:
					self._sources.append(file)
					kwm = self._build_matrix(file, Algorithms.TEXTRANK)
					self.add_matrix(kwm.get_title(), kwm)

		if isinstance(self._canvas, QLabel):
			self.update_canvas(list(self._matrices.values())[0])

	@QtCore.pyqtSlot(UserFocus)
	def handle_inbound_interaction(self, user_focus):
		super().handle_inbound_interaction(user_focus)
		if isinstance(user_focus, KeywordFocus) and user_focus.get_source() is Status.KEYWORD_SELECTION:
			node = user_focus.get_selected_node()
			self.matrix_interaction(node)

	@QtCore.pyqtSlot(Status)
	def cycle_canvas(self, status):
		self.update_canvas(self._matrices[super().get_navi_tool_bar().get_entry_field()])

	def update_canvas(self, matrix_):
		super().remove_inner_widget(self._canvas)
		if isinstance(self._mpl_tb, NavigationToolbar2QT):
			self._mpl_tb.close()
		self._canvas.close()
		self._canvas = MplCanvas(self, fig=matrix_.get_graph(), width=5, height=4, dpi=100)
		self._mpl_tb = NavigationToolbar2QT(self._canvas, self)
		super().add_inner_widget(self._mpl_tb)
		super().add_inner_widget(self._canvas)
		self._loaded_matrix = matrix_

	@QtCore.pyqtSlot(MatrixNode)
	def matrix_interaction(self, n):
		super().get_interaction_update_signal().emit(NodeFocus(n, self._loaded_matrix))

	def get_data_update_signal(self):
		return self._data_update


class MatrixEdge:

	def __init__(self, edge, origin_matrix_title):
		self._source = edge["source"]
		self._target = edge["target"]
		self._weight = edge["weight"] if "weight" in edge else 1
		self._origin = origin_matrix_title

	def set_source(self, s):
		self._source = s

	def set_target(self, t):
		self._target = t

	def set_weight(self, w_):
		self._weight = w_

	def get_source(self):
		return self._source

	def get_target(self):
		return self._target

	def get_weight(self):
		return self._weight


class KeywordEdge(MatrixEdge):

	def __init__(self, edge, origin_matrix_title):
		new_edge = {"source": edge[0], "target": edge[1]}

		super().__init__(new_edge, origin_matrix_title)
