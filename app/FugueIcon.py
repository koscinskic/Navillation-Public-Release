from enum import Enum

from PyQt5.QtGui import QIcon


class FugueIcon:

	def __init__(self, icon_enum):
		self.__base = "resources/images/"
		self.__ext = ".png"
		self.__icon = FugueIconRef[icon_enum]

	def __repr__(self):
		return f"{self.__base}{self.__icon.value}{self.__ext}"

	def get_icon(self):
		return QIcon(repr(self))


class FugueIconRef(Enum):
	RIGHT_ARROW = "arrow"
	LEFT_ARROW = "arrow-180"
