from collections import OrderedDict
import numpy as np
import spacy
from spacy.lang.en.stop_words import STOP_WORDS


def symmetrize(a):
	return a + a.T - np.diag(a.diagonal())


def get_token_pairs(window_size, sentences):
	"""Build token_pairs from windows in sentences"""
	token_pairs = list()
	for sentence in sentences:
		for i, word in enumerate(sentence):
			for j in range(i + 1, i + window_size):
				if j >= len(sentence):
					break
				pair = (word, sentence[j])
				if pair not in token_pairs:
					token_pairs.append(pair)
	return token_pairs


def get_matrix(vocab, token_pairs):
	"""Get normalized matrix"""
	# Build matrix
	vocab_size = len(vocab)
	g = np.zeros((vocab_size, vocab_size), dtype='float')
	for word1, word2 in token_pairs:
		i, j = vocab[word1], vocab[word2]
		g[i][j] = 1

	# Get Symmetric matrix
	g = symmetrize(g)

	# Normalize matrix by column
	norm = np.sum(g, axis=0)
	g_norm = np.divide(g, norm, where=norm != 0)  # this is to ignore the 0th element in norm

	return g_norm


def get_vocab(sentences):
	"""Get all tokens"""
	vocab = OrderedDict()
	i = 0
	for sentence in sentences:
		for word in sentence:
			if word not in vocab:
				vocab[word] = i
				i += 1
	return vocab


def sentence_segment(doc, candidate_pos=None, lower=False):
	"""Store those words only in candidate_pos"""
	sentences = []
	for sent in doc.sents:
		selected_words = []
		for token in sent:
			if candidate_pos is not None:
				if token.pos_ in candidate_pos and token.is_stop is False:
					if lower is True:
						selected_words.append(token.text.lower())
					else:
						selected_words.append(token.text)
			else:
				if token.pos_ != "SPACE":
					selected_words.append(token.text)
		sentences.append(selected_words)
	return sentences


class TextRankWrapper:
	"""Extract keywords from text"""

	def __init__(self, text):

		self._nlp = nlp = spacy.load('en_core_web_sm')

		self._cached_token_pairs = None

		self.d = 0.85  # damping coefficient, usually is .85
		self.min_diff = 1e-5  # convergence threshold
		self.steps = 10  # iteration steps
		self.node_weight = None  # save keywords and its weight

		self.analyze(text, candidate_pos=["NOUN", "PROPN"], window_size=4, lower=False)

	def get_node_weight(self):
		return self.node_weight

	def set_stopwords(self, stopwords):
		"""Set stop words"""
		for word in STOP_WORDS.union(set(stopwords)):
			lexeme = self._nlp.vocab[word]
			lexeme.is_stop = True

	def get_cached_token_pairs(self):
		return self._cached_token_pairs

	def get_keywords(self, number=10):
		"""Print top number keywords"""
		node_weight = OrderedDict(sorted(self.node_weight.items(), key=lambda t: t[1], reverse=True))
		for i, (key, value) in enumerate(node_weight.items()):
			print(key + ' - ' + str(value))
			if i > number:
				break

	def analyze(self, text,
	            candidate_pos=['NOUN', 'PROPN'],
	            window_size=4, lower=False, stopwords=list()):
		"""Main function to analyze text"""

		# Set stop words
		self.set_stopwords(stopwords)

		# Pare text by spaCy
		doc = self._nlp(text)

		# Filter sentences
		sentences = sentence_segment(doc, candidate_pos, lower)  # list of list of words

		# Build vocabulary
		vocab = get_vocab(sentences)

		# Get token_pairs from windows
		token_pairs = get_token_pairs(window_size, sentences)
		self._cached_token_pairs = token_pairs

		# Get normalized matrix
		g = get_matrix(vocab, token_pairs)

		# Initialization for weight(pagerank value)
		pr = np.array([1] * len(vocab))

		# Iteration
		previous_pr = 0
		for epoch in range(self.steps):
			pr = (1 - self.d) + self.d * np.dot(g, pr)
			if abs(previous_pr - sum(pr)) < self.min_diff:
				break
			else:
				previous_pr = sum(pr)

		# Get weight for each node
		node_weight = dict()
		for word, index in vocab.items():
			node_weight[word] = pr[index]

		self.node_weight = node_weight
