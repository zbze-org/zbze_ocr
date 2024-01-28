import ahocorasick
import marisa_trie


class WordTrie:
    def __init__(self, words):
        self.word_index_map = {word: id for id, word in enumerate(sorted(words))}
        self.word2word_id_trie = None
        self.aho_dawg = None
        self.reverse_aho_dawg = None

    def make(self):
        self.make_trie()
        self.make_automaton()
        self.make_reverse_automaton()

    def make_trie(self):
        self.word2word_id_trie = marisa_trie.RecordTrie(
            "I", [(word, (word_id,)) for word, word_id in self.word_index_map.items()]
        )

    @staticmethod
    def reverse_word(word):
        return word[::-1]

    def make_automaton(self):
        self.aho_dawg = ahocorasick.Automaton(key_type="str", value_type="int")
        for word, word_id in self.word_index_map.items():
            self.aho_dawg.add_word(word, word_id)

        self.aho_dawg.make_automaton()

    def make_reverse_automaton(self):
        self.reverse_aho_dawg = ahocorasick.Automaton(key_type="str", value_type="int")
        for word, word_id in self.word_index_map.items():
            self.reverse_aho_dawg.add_word(self.reverse_word(word), word_id)

        self.reverse_aho_dawg.make_automaton()

    @classmethod
    def calculate_from_file(cls, file_path):
        with open(file_path) as f:
            words = f.read().split("\n")

        return cls(words)

    def save(self, file_path):
        self.word2word_id_trie.save(file_path)

    def word_exists(self, word):
        return word in self.word2word_id_trie

    def get_words(self):
        return self.word2word_id_trie.keys()

    def get_word_id(self, word):
        word_id = self.word2word_id_trie.get(word, None)
        return word_id[0][0] if word_id else None

    def get_words_startswith_prefix(self, prefix):
        return self.word2word_id_trie.keys(prefix)

    def get_words_endswith_suffix(self, suffix):
        return self.word2word_id_trie.keys(suffix)

    def get_longest_prefix(self, word) -> str:
        return word[: self.aho_dawg.longest_prefix(word)]

    def get_longest_suffix(self, word):
        return self.reverse_word(self.get_longest_prefix(self.reverse_word(word)))
