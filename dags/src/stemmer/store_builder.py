import os
import pickle
from collections import defaultdict

import marisa_trie
from tqdm import tqdm

from dags.src.stemmer.rules.base import create_template_group_rule
from dags.src.stemmer.stemmer import Stemmer
from dags.src.stemmer.store import StemmerData


def calculate_word2template(words_file_path, template_groups_file_path):
    with open(words_file_path, "r") as f:
        words = f.read().split("\n")

    group_rules = create_template_group_rule(template_groups_file_path)
    stemmer = Stemmer(rules=[rule for g, rule in sorted(group_rules.items(), key=lambda x: x[0], reverse=True)])

    word2templates = defaultdict(list)
    for word in tqdm(words):
        templates = stemmer.find_suitable_templates(word)
        word2templates[word].extend(templates)
    return word2templates


def build_trie_stemmer_data(words_file_path, template_groups_file_path, output_file_path):
    word2templates = calculate_word2template(words_file_path, template_groups_file_path)

    word_index_map = {}
    word_id2template_ids = defaultdict(list)
    template2index = {}
    for word_index, (word, templates) in enumerate(tqdm(word2templates.items()), start=1):
        word_index_map[word] = word_index  # связь слово - id слова
        for template in templates:
            if template not in template2index:
                template2index[template] = len(template2index) + 1  # связь шаблонов - id шаблона
            word_id2template_ids[word_index].append(template2index[template])  # связь id слово - id шаблонов

    template2template_id_trie = marisa_trie.RecordTrie(
        "I",
        [(template, (template_id,)) for template, template_id in template2index.items()],
    )
    word2word_id_trie = marisa_trie.RecordTrie("I", [(word, (word_id,)) for word, word_id in word_index_map.items()])
    data = StemmerData(
        word2word_id_trie=word2word_id_trie,
        template2template_id_trie=template2template_id_trie,
        word_id2template_ids=word_id2template_ids,
    )
    with open(output_file_path, "wb") as f:
        pickle.dump(data, f)

    return data
