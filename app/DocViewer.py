from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QListView, QListWidget, QListWidgetItem

from app.DocumentUpdate import DocumentUpdate
from app.MatrixViewer import KeywordMatrix
from app.NaviDock import NaviTool
from app.Status import Status
from app.UserFocus import UserFocus, NodeFocus, KeywordFocus
from nlp.DocUtils import DocUtils


class DocViewer(NaviTool):

	_update_ready = pyqtSignal(DocumentUpdate)
	# _document_interaction_ready = pyqtSignal(QListWidgetItem)

	def __init__(self, resolution=None):

		super().__init__("Doc Viewer", resolution=resolution)

		self._document_view = QLabel("Open a File to Begin Analyzing")
		self._last_focus = None

		# TODO: universal config
		self.__keyword_target_color = "#7F0000"  # Dark Red
		self.__keyword_color = "#0026FF"  # Dark Blue

		self._update_ready.connect(self.update_document_view)

		super().add_inner_widget(self._document_view)

	# def aggregate_salient_sentences(self):
	#
	# 	files = self.get_file_handler().get_files()
	#
	# 	for document in files:
	# 		du = DocUtils(files[document])

	def refresh(self, status):

		super().refresh(status)

		# Clear Initial Tooltip
		if status is Status.ADD and isinstance(self._document_view, QLabel):

			text = super().get_file_handler().get_files()[list(super().get_file_handler().get_files())[0]]
			self._update_ready.emit(DocumentUpdate(text, None, None))

	@QtCore.pyqtSlot(UserFocus)
	def handle_inbound_interaction(self, user_focus):
		super().handle_inbound_interaction(user_focus)

		if isinstance(user_focus, NodeFocus) and user_focus.get_source() is Status.NODE_SELECTION:
			text = super().get_file_handler().get_files()[user_focus.get_selected_matrix().get_origin_file()]
			self._update_ready.emit(DocumentUpdate(text, user_focus, Status.DOCUMENT_UPDATE_READY))

	@QtCore.pyqtSlot(DocumentUpdate)
	def update_document_view(self, doc_update):

		base_text = doc_update.get_base_text()
		user_focus = doc_update.get_user_focus()

		# if isinstance(self._document_view, QListWidget):
		# 	self._document_view.clearSelection()
		# 	self._document_view.itemClicked.disconnect(self.document_interaction)
		# 	self._document_view.clear()

		doc_utils = None
		keywords = []
		target = None

		if user_focus is not None:
			self._last_focus = user_focus
			target = self._last_focus.get_selected_node().get_keyword()
			keywords = [k.get_keyword() for k in self._last_focus.get_selected_matrix().get_nodes()]
			doc_utils = DocUtils(base_text, keywords)
		else:
			doc_utils = DocUtils(base_text)

		list_ = QListWidget()
		list_.itemClicked.connect(self.document_interaction)

		for sentence in doc_utils.get_sentences():
			for token in sentence:
				stylized_token = QListWidgetItem(token.text)
				if token.text == target:
					stylized_token.setBackground(QColor(self.__keyword_target_color))
				elif token.text in keywords:
					stylized_token.setBackground(QColor(self.__keyword_color))
				list_.addItem(stylized_token)

		list_.setFlow(QListView.LeftToRight)
		list_.setWrapping(True)

		super().remove_inner_widget(self._document_view)
		# self._document_view.close()
		self._document_view.deleteLater()
		self._document_view = list_
		super().add_inner_widget(self._document_view)

	@QtCore.pyqtSlot(QListWidgetItem)
	def document_interaction(self, word_item):

		matrix = self._last_focus.get_selected_matrix()

		if isinstance(matrix, KeywordMatrix):

			keyword_entry = matrix.get_keyword_entry(word_item.text())
			if keyword_entry is not None:
				focus = KeywordFocus(keyword_entry, matrix)
				super().get_interaction_update_signal().emit(focus)
