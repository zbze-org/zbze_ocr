import nltk


class NGramAnalyzer:
    def __init__(self, words, ngrams=(2, 3)):
        self.words = words
        self.ngrams = ngrams

        for n in ngrams:
            setattr(self, f"n{n}_gram_fd", self._create_freq_dist(words, n))

    @classmethod
    def word_to_ngrams(cls, word, n):
        return ["".join(gram) for gram in nltk.ngrams(word, n)]

    @classmethod
    def _create_freq_dist(cls, words, n):
        return nltk.FreqDist(
            [gram for word in words for gram in cls.word_to_ngrams(word, n)]
        )

    def _ngram_freq_treshold(self, ngram, treshold):
        return getattr(self, f"n{len(ngram)}_gram_fd")[ngram] < treshold

    def treshold_ngram(self, word, treshold, n=3):
        ngrams = self.word_to_ngrams(word, n)
        if not ngrams:
            return 0

        return sum(
            [self._ngram_freq_treshold(gram, treshold) for gram in ngrams]
        ) / len(ngrams)

    def treshold_ngram_mean(self, word, treshold, n=3):
        ngrams = self.word_to_ngrams(word, n)
        if not ngrams:
            return 0

        return sum(
            [self._ngram_freq_treshold(gram, treshold) for gram in ngrams]
        ) / len(ngrams)
