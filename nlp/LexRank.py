from lexrank import STOPWORDS, LexRank


class LexRankWrapper:

    """
    :param base_corpus_sentences - list of docs, of which are list of sentences
    :param target_sentences - list of sentences for target doc
    """
    def __init__(self, base_corpus_sentences, target_sentences):

        lxr = LexRank(base_corpus_sentences, stopwords=STOPWORDS['en'])

        # get summary with classical LexRank algorithm
        self._summary = lxr.get_summary(target_sentences, summary_size=2, threshold=.1)

        # get summary with continuous LexRank
        self._continuous_summary = lxr.get_summary(target_sentences, threshold=None)

        # get LexRank scores for sentences
        # 'fast_power_method' speeds up the calculation, but requires more RAM
        self._scores = lxr.rank_sentences(
            target_sentences,
            threshold=None,
            fast_power_method=False,
        )

    def get_summary(self):
        return self._summary

    def get_continuous_summary(self):
        return self._continuous_summary

    def get_scores(self):
        return self._scores
