import os
import pickle
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

import ahocorasick
import marisa_trie
from fuzzywuzzy import fuzz
from tokenizers import Tokenizer
from tqdm import tqdm

from dags.src.stemmer.rules.base import TemplateGroupTrieBasedRule

tokenizer_unigram_5k = Tokenizer.from_file(os.path.join("../dags/src/spellcheck/data/", "tokenizer_unigram_5k.json"))


@dataclass
class StemmerData:
    # для эффективного хранения данных (оптимизация по диску текстовых ключей)
    word2word_id_trie: marisa_trie.RecordTrie
    template2template_id_trie: marisa_trie.RecordTrie
    # связь id слово - id шаблонов
    word_id2template_ids: Dict[int, List[int]]
    # будем распаковывать в память дерево template2template_id_trie
    word_id2word: Optional[Dict[int, str]] = None
    template_id2template: Optional[Dict[int, str]] = None
    word2word_id_dawg: Optional[ahocorasick.Automaton] = None
    tokenizer: Optional[Tokenizer] = None
    tokenized_index: Optional[Dict[str, List[int]]] = None
    prefixes: Optional[Dict[str, int]] = None
    suffixes: Optional[Dict[str, int]] = None


class StemmerStore:
    data: StemmerData
    stem_rule: TemplateGroupTrieBasedRule

    def __init__(self, data=None):
        self.data = data
        if self.data:
            self.check_data(self.data)

    @staticmethod
    def check_data(data):
        if not isinstance(data, StemmerData):
            raise ValueError("data must be StemmerData")
        if not data.word2word_id_trie:
            raise ValueError("word2word_id_trie must be not empty")
        if not data.template2template_id_trie:
            raise ValueError("template2template_id_trie must be not empty")
        if not data.word_id2template_ids:
            raise ValueError("word_id2template_ids must be not empty")

    def _fill_word_id2word(self):
        self.data.word_id2word = {word_id: word for word, (word_id,) in self.data.word2word_id_trie.items()}

    def _fill_template_id2template(self):
        self.data.template_id2template = {
            template_id: template for template, (template_id,) in self.data.template2template_id_trie.items()
        }

    def _fill_aho_corasick(self):
        word2word_id_dawg = ahocorasick.Automaton(key_type="str", value_type="int")

        for word, word_id in tqdm(self.data.word2word_id_trie.items()):
            word2word_id_dawg.add_word(word, word_id[0])

        word2word_id_dawg.make_automaton()
        self.data.word2word_id_dawg = word2word_id_dawg

    def _fill_tokenizer(self, tokenizer_path=None):
        self.data.tokenizer = tokenizer_unigram_5k

    def _fill_tokenized_index(self):
        self.data.tokenized_index = defaultdict(set)
        for word, word_id in tqdm(self.data.word2word_id_trie.items()):
            tokens_ids = self.data.tokenizer.encode(word).ids
            for token_id in tokens_ids:
                self.data.tokenized_index[token_id].add(word_id[0])

    def _fill_prefixes(self, limit=2000):
        prefixes = []
        for word, _ in tqdm(self.data.word2word_id_trie.items()):
            for i in range(1, len(word)):
                prefixes.append(word[:i])
        cnt = Counter(prefixes)
        self.data.prefixes = dict(cnt.most_common(limit))

    def _fill_suffixes(self, limit=2000):
        suffixes = []
        for word, _ in tqdm(self.data.word2word_id_trie.items()):
            for i in range(1, len(word)):
                suffixes.append(word[-i:])
        cnt = Counter(suffixes)
        self.data.suffixes = dict(cnt.most_common(limit))

    def fill_data(self):
        self._fill_word_id2word()
        self._fill_template_id2template()
        self._fill_aho_corasick()
        self._fill_tokenizer()
        self._fill_tokenized_index()
        self._fill_prefixes()
        self._fill_suffixes()

    def load_data_from_file(self, data_file_path):
        with open(data_file_path, "rb") as f:
            data = pickle.load(f)

        self.check_data(data)
        self.data = data
        # досчитаем нужные структуры данных
        self.fill_data()
        self.stem_rule = TemplateGroupTrieBasedRule(
            word2word_id_trie=self.data.word2word_id_trie,
            template2template_id_trie=self.data.template2template_id_trie,
            word_id2template_ids=self.data.word_id2template_ids,
        )

    def _get_word_id(self, word):
        word_id = self.data.word2word_id_trie.get(word, None)
        return word_id[0][0] if word_id else None

    def _get_template_id(self, template):
        template_id = self.data.template2template_id_trie.get(template, None)
        return template_id[0][0] if template_id else None

    def _get_template_ids(self, word_id):
        return self.data.word_id2template_ids.get(word_id, [])

    def get_templates(self, word):
        self.check_data(self.data)

        word_id = self._get_word_id(word)
        if word_id is None:
            return []

        template_ids = self._get_template_ids(word_id)
        if not template_ids:
            return []

        templates = []
        for template_id in template_ids:
            template = self.data.template_id2template.get(template_id, None)
            if template is not None:
                templates.append(template)

        return templates

    def find_possible_stems(self, word, exist_only=False):
        possible_stems = self.stem_rule.find_possible_stems(word)
        if exist_only:
            possible_stems = [stem for stem in possible_stems if self._get_word_id(stem)]

        return possible_stems

    def find_by_prefix(self, prefix):
        """
        prefix: тхузэмыгъэ
        return: [('тхузэмыгъэзахуэу', (267808,)), ('тхузэмыгъэкIуу', (164769,))]
        :param prefix:
        :return:
        """
        self.check_data(self.data)
        return self.data.template2template_id_trie.keys(prefix)

    def find_by_suffix(self, suffix, prefix_len=3, affix_exactly=False):
        """
        suffix: эфIэкIынут
        prefix_len: 3
        query_mask: ???эфIэкIынут
        return:
        [('хузэфIэкIынут', 36107),
         ('хузэфIэкIынутэкъым', 36478),
         ('хузэфIэкIынутэкъыми', 143430),
         ('щызэфIэкIынутэкъым', 429094),
         ('ХузэфIэкIынутэкъым', 379224)]
        :param affix_exactly:
        :param suffix:
        :return:
        """
        self.check_data(self.data)
        prefix = "?" * prefix_len
        how = ahocorasick.MATCH_EXACT_LENGTH if affix_exactly else ahocorasick.MATCH_AT_LEAST_PREFIX

        return self.data.word2word_id_dawg.items(f"{prefix}{suffix}", "?", how)

    def find_sub_words(self, word):
        """
        word: тхузэфIэкIынут
        return:
        [('т', 6469),
         ('тх', 194093),
         ('тху', 5986),
         ('тхузэфIэкI', 27992),
         ('тхузэфIэкIын', 121246),
         ('тхузэфIэкIыну', 22258),
         ('тхузэфIэкIынут', 117580)]
        :param word:
        :return:
        """
        self.check_data(self.data)

        return self.data.word2word_id_dawg.items(word, "?", ahocorasick.MATCH_AT_MOST_PREFIX)

    def _get_word_by_id(self, word_id):
        return self.data.word_id2word[word_id]

    def _get_tokens(self, word):
        encode = self.data.tokenizer.encode(word)
        return zip(encode.ids, encode.tokens)

    def _get_word_ids_by_token_id(self, token_id):
        # забираем все слова из индекса, которые содержат этот токен
        return self.data.tokenized_index[token_id]

    def search_in_tokenized_index(self, word, min_ratio=80, token_limit=0, word_limit_in_step=100):
        """
        поиск по токенизированному индексу. Пересечение списков слов, которые содержат токены из исходного слова
        Сортировка токенов важна, чтобы сначала искать по более популярным токенам (менее значимым)
        Тем самым мы получаем более ролевантные результаты на последних шагах, где список слов уже не такой большой

        :param token_limit:
        :param word:
        :param min_ratio:
        :return:
        """
        self.check_data(self.data)

        results = {}
        result_word_ids = None

        tokens = self._get_tokens(word)
        sorted_tokens = sorted(tokens, key=lambda x: x[0])
        if token_limit:
            sorted_tokens = sorted_tokens[-token_limit:]

        for step, (token_id, token) in enumerate(sorted_tokens):
            if step == 0:
                result_word_ids = self._get_word_ids_by_token_id(token_id)
            else:
                result_word_ids = result_word_ids.intersection(self._get_word_ids_by_token_id(token_id))

            if len(result_word_ids) < word_limit_in_step:
                step_results = {
                    self._get_word_by_id(word_id): fuzz.ratio(word, self._get_word_by_id(word_id))
                    for word_id in result_word_ids
                }
                results.update({word: ratio for word, ratio in step_results.items() if ratio >= min_ratio})

        return sorted(results.items(), key=lambda x: x[1], reverse=True)

    def calc_stem(self, word, sw_min_len=3):
        possible_stems = self.stem_rule.find_possible_stems(word)
        sub_words = []
        for stem in possible_stems:
            for w, ratio in self.search_in_tokenized_index(stem):
                for sw, sw_id in self.find_sub_words(w):
                    if sw not in self.data.prefixes and len(sw) >= sw_min_len:
                        sub_words.append(sw)

        cnt = Counter(sub_words)
        return cnt.most_common(1)
