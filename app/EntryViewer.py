from IPython.external.qt_for_kernel import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser, QListWidget, QListWidgetItem, QListView, \
	QGroupBox, QScrollArea

from app.MatrixViewer import VisualMatrix
from app.NaviDock import NaviTool, NaviDock
from app.Status import Status
from app.UserFocus import UserFocus, NodeFocus
from nlp.DocUtils import DocUtils


class EntryViewer(NaviTool):

	def __init__(self, data_update_signal, resolution=None):

		super().__init__("Entry Viewer", resolution=resolution)

		self._data_update = data_update_signal
		self._data_update.connect(self.process_matrix)

		self._source_matrices = {}
		self._keyword_analysis = {}
		self._entries = {}

		# TODO: better in-app instruction set
		self._entry_container = QLabel("Select a Node to begin Analyzing")
		super().add_inner_widget(self._entry_container)

	@QtCore.pyqtSlot(VisualMatrix)
	def process_matrix(self, matrix):

		matrix_title = matrix.get_title()
		matrix_type = matrix_title.split("_")[1]
		source_text = super().get_file_handler().get_files()[matrix.get_origin_file()]

		if matrix_type == "keyword":
			keywords = [k.get_keyword() for k in matrix.get_nodes()]
			self.process_keyword_matrix(source_text, keywords, matrix_title)

	def process_keyword_matrix(self, text, keywords, origin_matrix_title):

		doc_utils = DocUtils(text, keywords)
		# TODO: better data container
		self._keyword_analysis[origin_matrix_title] = (
			doc_utils.get_annotated_sentences(), doc_utils.get_keyword_entries(), keywords
		)

	@QtCore.pyqtSlot(UserFocus)
	def handle_inbound_interaction(self, user_focus):
		super().handle_inbound_interaction(user_focus)
		if isinstance(user_focus, NodeFocus) and user_focus.get_source() is Status.NODE_SELECTION:
			node = user_focus.get_selected_node()
			self.generate_sentence_entries(node.get_keyword(), node.get_origin())

	def generate_sentence_entries(self, target_keyword, origin_matrix_title):

		self._entries[origin_matrix_title] = []

		sentences = self._keyword_analysis[origin_matrix_title][1][target_keyword]
		for s in sentences:
			self._entries[origin_matrix_title].append(
				SentenceEntry(
					s,
					target_keyword,
					self._keyword_analysis[origin_matrix_title][0][s],
					[self.get_resolution()[0] * 0.25, self.get_resolution()[1] * 0.2]
				)
			)

		self.display_entries(self._entries[origin_matrix_title])

	def display_entries(self, entries):

		if isinstance(self._entry_container, QLabel):
			super().remove_inner_widget(self._entry_container)
			self._entry_container.close()
			self._entry_container = EntryContainer([self.get_resolution()[0] * 0.3, self.get_resolution()[1] * 0.7])
			scroll_area = QScrollArea()
			scroll_area.setWidget(self._entry_container)
			scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
			super().add_inner_widget(scroll_area)
		else:
			self._entry_container.clear_entries()

		for e in entries:
			self._entry_container.add_entry(e)


class EntryContainer(QWidget):

	def __init__(self, dimensions):

		super().__init__()

		self._dimensions = dimensions
		self.setFixedWidth(self._dimensions[0])
		self.setMinimumHeight(self._dimensions[1])

		self._entries = []

		self._outer_layout = QVBoxLayout()
		self.setLayout(self._outer_layout)

	def add_entry(self, entry):
		self._entries.append(entry)
		self._outer_layout.addWidget(entry)
		self.setFixedHeight((entry.get_dimensions()[1] * 1.01) * len(self._entries))

	def clear_entries(self):
		for e in self._entries:
			e.close()
		self._entries = []
		# self.setMinimumHeight(self._dimensions[1])


# TODO: generalize
class SentenceEntry(QWidget):

	def __init__(self, sentence_entry, target_keyword, keywords, dimensions):

		super().__init__()

		self._dimensions = dimensions

		self.setFixedWidth(dimensions[0])
		self.setFixedHeight(dimensions[1])

		# TODO: universal config
		self.__keyword_target_color = "#7F0000"  # Dark Red
		self.__keyword_color = "#0026FF"  # Dark Blue

		self._entry = sentence_entry
		self._target = target_keyword
		self._keywords = keywords

		self._outer_layout = QVBoxLayout()
		self.setLayout(self._outer_layout)

		self._entry_browser = QTextBrowser()
		self._entry_browser.setText(self._entry.text)
		self._target_label = QLabel(f"Target Keyword: {self._target}")

		self._shared_keywords = QListWidget()

		for keyword in keywords:
			stylized_token = QListWidgetItem(keyword)
			if keyword == target_keyword:
				stylized_token.setBackground(QColor(self.__keyword_target_color))
			else:
				stylized_token.setBackground(QColor(self.__keyword_color))
			self._shared_keywords.addItem(stylized_token)

		self._shared_keywords.setFlow(QListView.LeftToRight)
		self._shared_keywords.setWrapping(True)

		self._outer_layout.addWidget(self._target_label)
		self._outer_layout.addWidget(QLabel("Sentence Entry:"))
		self._outer_layout.addWidget(self._entry_browser)
		self._outer_layout.addWidget(QLabel("Related Keywords:"))
		self._outer_layout.addWidget(self._shared_keywords)

	def get_dimensions(self):
		return [self.width(), self.height()]
