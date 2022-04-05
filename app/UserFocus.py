from app.Status import Status


class UserFocus:

	def __init__(self, source=None):
		self._source = source

	def set_source(self, s):
		self._source = s

	def get_source(self):
		return self._source


class NodeFocus(UserFocus):

	def __init__(self, node=None, matrix=None):

		# TODO: streamlined source identification
		super().__init__(source=Status.NODE_SELECTION)

		self._selected_node = node
		self._selected_matrix = matrix

	def get_selected_node(self):
		return self._selected_node

	def get_selected_matrix(self):
		return self._selected_matrix


class KeywordFocus(NodeFocus):

	def __init__(self, node, matrix):

		super().__init__(node, matrix)

		self.set_source(Status.KEYWORD_SELECTION)
