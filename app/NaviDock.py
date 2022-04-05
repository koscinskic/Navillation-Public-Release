from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from app.FileHandler import FileHandler
from app.FugueIcon import FugueIcon
from app.Status import Status
from app.UserFocus import UserFocus, NodeFocus


class NaviDock(QWidget):

	_file_updates = pyqtSignal(Status)
	_interaction_updates = {}

	def __init__(self, resolution, parent=None):

		super().__init__()

		# TODO: better universal config
		self._resolution = resolution
		self._w = self._resolution[0]
		self._h = self._resolution[1]

		self._outer_layout = QHBoxLayout()
		self.setLayout(self._outer_layout)

		self._file_handler = FileHandler(self, self._file_updates)
		self._navi_tools = []

		self._file_updates.connect(self.refresh_dock)

	def add_navi_tool(self, new_tool):

		signal = new_tool.get_interaction_update_signal()

		# global
		signal.connect(self.handle_global_interaction)
		self._interaction_updates[new_tool.get_navi_tool_name()] = signal

		# local
		for cached_tool in self._navi_tools:
			# new signal -> old tools
			signal.connect(cached_tool.handle_inbound_interaction)
			# old signal -> new tool
			cached_tool.get_interaction_update_signal().connect(new_tool.handle_inbound_interaction)

		new_tool.set_file_handler(self._file_handler)
		self._outer_layout.addWidget(new_tool)
		self._navi_tools.append(new_tool)

		new_tool.setMaximumHeight(self._h * 0.8)

		tool_ct = len(self._navi_tools)
		for cached_tool in self._navi_tools:
			cached_tool.setMaximumWidth(self._w / tool_ct)

	@QtCore.pyqtSlot(UserFocus)
	def handle_global_interaction(self, user_focus):
		pass

	@QtCore.pyqtSlot(Status)
	def refresh_dock(self, status):

		for tool in self._navi_tools:
			tool.refresh(status)

	def get_file_handler(self):
		return self._file_handler

	def get_file_updates_signal(self):
		return self._file_updates


class NaviTool(QWidget):

	_interaction_update = pyqtSignal(UserFocus)

	def __init__(self, name, file_handler=None, parent=None, user_focus_signal=None, resolution=None):

		super().__init__(parent)

		self._resolution = resolution

		self._file_handler = file_handler

		self._user_focus_signal = user_focus_signal

		if user_focus_signal is not None:
			self._user_focus_signal.connect(self.handle_inbound_interaction)

		self._navi_tool_name = name

		self._outer_layout = QVBoxLayout()
		self.setLayout(self._outer_layout)

		self._navi_tool_name_label = QLabel(name)
		self._outer_layout.addWidget(self._navi_tool_name_label)

		self._navi_tool_bar = NaviToolBar()
		self._outer_layout.addWidget(self._navi_tool_bar)

		self._navi_tool_space = NaviToolSpace()
		self._outer_layout.addWidget(self._navi_tool_space)

	@QtCore.pyqtSlot(UserFocus)
	def handle_inbound_interaction(self, user_focus):
		# print(f"Reporting Tool: {self._navi_tool_name} \t Interaction Source: {user_focus.get_source()}")
		pass

	def add_tool_bar_widget(self, widget):
		self._navi_tool_bar.add_widget(widget)

	def add_inner_widget(self, widget):
		self._navi_tool_space.add_widget(widget)

	def remove_inner_widget(self, widget):
		self._navi_tool_space.remove_widget(widget)

	def set_file_handler(self, file_handler):
		self._file_handler = file_handler

	def get_interaction_update_signal(self):
		return self._interaction_update

	def get_file_handler(self):
		return self._file_handler

	def get_navi_tool_name(self):
		return self._navi_tool_name

	def get_navi_tool_bar(self):
		return self._navi_tool_bar

	def refresh(self, status):
		pass

	def get_resolution(self):
		return self._resolution


class NaviToolBar(QWidget):

	_navigation_update = pyqtSignal(Status)

	def __init__(self, parent=None):

		super().__init__(parent)

		self._entries = []
		self._entry_field = None

		self._outer_layout = QHBoxLayout()
		self.setLayout(self._outer_layout)

		self._previous_btn = QPushButton()
		self._previous_btn.clicked.connect(self.previous)
		self._previous_btn.setIcon(FugueIcon("LEFT_ARROW").get_icon())
		self._outer_layout.addWidget(self._previous_btn)

		self._entry_lbl = QLabel()
		self._outer_layout.addWidget(self._entry_lbl)

		self._next_btn = QPushButton()
		self._next_btn.clicked.connect(self.next)
		self._next_btn.setIcon(FugueIcon("RIGHT_ARROW").get_icon())
		self._outer_layout.addWidget(self._next_btn)

	def previous(self):

		previous = self._entries.index(self._entry_field) - 1

		if previous <= 0:
			self.update_entry_field(self._entries[0])
		else:
			self.update_entry_field(self._entries[previous])

		self._navigation_update.emit(Status.PREVIOUS)

	def next(self):

		next_ = self._entries.index(self._entry_field) + 1

		if next_ >= len(self._entries) - 1:
			self.update_entry_field(self._entries[-1])
		else:
			self.update_entry_field(self._entries[next_])

		self._navigation_update.emit(Status.NEXT)

	def update_entry_field(self, content):
		self._entry_field = content
		self._entry_lbl.setText(self._entry_field)

	def add_entry(self, entry):

		if entry not in self._entries:
			self._entries.append(entry)

		if self._entry_field is None:
			self.update_entry_field(self._entries[0])

	# TODO: safe-navigation for last delete
	def remove_entry(self, entry):

		if entry in self._entries:
			self._entries.pop(entry)

	def get_entry_field(self):
		return self._entry_field

	def get_navigation_update_signal(self):
		return self._navigation_update


class NaviToolSpace(QWidget):

	def __init__(self, parent=None):

		super().__init__(parent)

		self._outer_layout = QVBoxLayout()
		self.setLayout(self._outer_layout)

	def add_widget(self, widget):
		self._outer_layout.addWidget(widget)

	def remove_widget(self, widget):
		self._outer_layout.removeWidget(widget)
