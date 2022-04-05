from PyQt5.QtWidgets import QFileDialog

from app.Status import Status


class FileHandler:

	# Identified by Title
	_files = {}

	def __init__(self, host_widget, update_signal):

		self._host_widget = host_widget
		self._update_signal = update_signal

	def _retrieve_files(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		files, _ = QFileDialog.getOpenFileNames(self._host_widget,
		                                        "QFileDialog.getOpenFileNames()",
		                                        "",
		                                        "All Files (*);;Python Files (*.py)",
		                                        options=options)
		return files

	def add_files_option(self):

		files = self._retrieve_files()

		# TODO: null and duplicate case handling
		for file in files:
			self.add_file(file)

		self._update_signal.emit(Status.ADD)

	# TODO: empty set handling
	def delete_files_option(self):

		files = self._retrieve_files()
		for file in files:
			self.remove_file(file)
		self._update_signal.emit(Status.DELETE)

	def add_file(self, file_path):

		file_name = parse_file_path(file_path)

		if file_name not in self._files:
			with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
				self._files[file_name] = f.read()

	def remove_file(self, file_name):

		if file_name in self._files:
			self._files.pop(file_name)

	def get_files(self):
		return self._files


def parse_file_path(file_path):
	return file_path.split('/')[-1].split('.')[0]
