import spacy

from nlp.TextRank import sentence_segment


def _filter_sentences(sentence_reference, keywords):

	# TODO: better naming
	sentence_lead = {}
	keyword_lead = {}

	for sentence in sentence_reference.keys():
		for word in sentence_reference[sentence]:
			if word in keywords:
				if word in keyword_lead:
					if sentence not in keyword_lead[word]:
						keyword_lead[word].append(sentence)
				else:
					keyword_lead[word] = [sentence]
				if sentence in sentence_lead:
					if word not in sentence_lead[sentence]:
						sentence_lead[sentence].append(word)
				else:
					sentence_lead[sentence] = [word]

	return sentence_lead, keyword_lead


class DocUtils:

	def __init__(self, text, keywords=None):

		self._nlp = spacy.load("en_core_web_sm")

		self._text = text
		self._keywords = keywords

		self._sentences = [s for s in self._nlp(text).sents]
		self._sentence_reference = {}
		self._segmented_sentences = sentence_segment(self._nlp(text))

		for i in range(len(self._segmented_sentences)):
			self._sentence_reference[self._sentences[i]] = self._segmented_sentences[i]

		# TODO: better naming
		if keywords is not None:
			self._annotated_sentences, self._keyword_entries = _filter_sentences(self._sentence_reference, self._keywords)

	def get_sentence_reference(self):
		return self._sentence_reference

	def get_sentences(self):
		return self._sentences

	# strings as opposed to Spacy Tokens
	def get_raw_sentences(self):
		sentences = []
		for span in self.get_sentences():
			new_span = []
			for token in span:
				if token.pos_ != "SPACE":
					new_span.append(token.text)
			if len(span) > 0:
				sentences.append(" ".join(new_span))
		return sentences

	def get_annotated_sentences(self):
		return self._annotated_sentences

	def get_keyword_entries(self):
		return self._keyword_entries
