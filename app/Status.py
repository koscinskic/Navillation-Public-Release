from enum import Enum


class Status(Enum):
	ADD = "add"
	DELETE = "delete"
	PREVIOUS = "previous"
	NEXT = "next"
	NODE_SELECTION = "node selection"
	KEYWORD_SELECTION = "keyword selection"
	DOCUMENT_UPDATE_READY = "doc update ready"
