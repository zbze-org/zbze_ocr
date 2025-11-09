import json
import re
from collections import Counter


def min_length_condition(word, min_length=3):
    return len(word) >= min_length


def startswith_condition(word, start):
    return word.startswith(start)


def endswith_condition(word, ending):
    return word.endswith(ending)


def match_condition(word, pattern):
    return re.match(pattern, word)


class BaseRule:
    min_length = 2

    def __init__(self, pattern, conditions=None, excluded_words=None, priority=0):
        self.pattern = pattern
        self._pattern_length = len(pattern.replace("$", ""))
        self.conditions = conditions or []
        self.regex = re.compile(pattern)
        self.excluded_words = excluded_words or []
        self.priority = priority

    def is_valid_stem_length(self, word):
        return len(word) - self._pattern_length >= self.min_length

    def is_word_in_excluded_words(self, word):
        return word in self.excluded_words

    def check_all_extra_conditions(self, word):
        return all(condition(word) for condition in self.conditions)

    def is_applicable(self, word):
        return (
            self.is_valid_stem_length(word)
            and not self.is_word_in_excluded_words(word)
            and self.check_all_extra_conditions(word)
        )

    def apply(self, word):
        if self.is_applicable(word):
            return self.regex.sub("", word), True
        return word, False


rule_group_1 = [
    BaseRule(
        pattern="хэри$",
        conditions=[
            lambda x: min_length_condition(x, min_length=6),
        ],
        priority=3,
    ),
    BaseRule(
        pattern="ри$",
        conditions=[
            lambda x: min_length_condition(x, min_length=4),
        ],
        excluded_words=["ахэри"],
        priority=2,
    ),
    BaseRule(
        pattern="и$",
        conditions=[
            lambda x: min_length_condition(x, min_length=3),
        ],
        priority=1,
    ),
]


def template_to_regex(template):
    template = re.sub(r"\*{2,}", "*", template)
    template = re.sub(r"\*", ".+", template)
    template = "^" + template + "$"
    return re.compile(template)


def template_to_extract_group_regex(template):
    return re.compile(template.replace("*", "(.+)"))


class TemplateGroupRule:
    min_length = 3

    def choose_template(self, word):
        raise NotImplementedError

    def is_applicable(self, stem, word):
        return len(stem) >= self.min_length

    def try_apply_template(self, template, word):
        extract_group_regex = template_to_extract_group_regex(template)
        stem = extract_group_regex.sub(r"\1", word)
        if self.is_applicable(stem, word):
            return stem, True
        return word, False

    def apply(self, word):
        for template in self.choose_template(word):
            stem, applied = self.try_apply_template(template, word)
            if applied:
                return stem, True

        return word, False

    def find_possible_stems(self, word):
        possible_stems = []
        for template in self.choose_template(word):
            stem, applied = self.try_apply_template(template, word)
            if applied:
                possible_stems.append(stem)
        return possible_stems

    def find_suitable_templates(self, word):
        suitable_templates = []
        for template in self.choose_template(word):
            if not template:
                continue
            stem, applied = self.try_apply_template(template, word)
            if applied:
                suitable_templates.append(template)
        return suitable_templates

    def find_possible_stems_lvl_recursive(self, word, level=0, max_level=2):
        possible_stems_unique = set()

        level_possible_stems = self.find_possible_stems(word)
        for stem in level_possible_stems:
            if (word, stem) not in possible_stems_unique:
                possible_stems_unique.add((word, stem))
                yield level, (word, stem)

        if level < max_level:
            for stem in level_possible_stems:
                yield from self.find_possible_stems_lvl_recursive(stem, level=level + 1, max_level=max_level)

    def get_most_common_stems(self, word, stems_limit=1, max_level=2):
        stems = []
        for level, (word, stem) in self.find_possible_stems_lvl_recursive(word, max_level=max_level):
            stems.append(stem)

        cnt = Counter(stems)
        return cnt.most_common(stems_limit)


class TemplateGroupRegexpRule(TemplateGroupRule):
    min_length = 3

    def __init__(self, templates):
        self.templates = templates
        self.regexps = [template_to_regex(template) for template in templates]

    def choose_template(self, word):
        for template, regexp in zip(self.templates, self.regexps):
            if regexp.match(word):
                yield template
        return None


class TemplateGroupTrieBasedRule(TemplateGroupRule):
    def __init__(self, word2word_id_trie, template2template_id_trie, word_id2template_ids):
        self.word2word_id_trie = word2word_id_trie
        self.template2template_id_trie = template2template_id_trie
        self.word_id2template_ids = word_id2template_ids
        self.template_id2template = {
            template_id[0]: template for template, template_id in template2template_id_trie.items()
        }

    def choose_template(self, word):
        word_id = self.word2word_id_trie.get(word, None)
        if word_id is None:
            return None

        word_id = word_id[0][0]
        template_ids = self.word_id2template_ids.get(word_id, [])

        for template_id in template_ids:
            template = self.template_id2template.get(template_id, None)
            if template is not None:
                yield template
        return None


def create_template_group_rule(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    template_groups_rules = {}
    for template_group in sorted(data, key=lambda x: x["length"], reverse=True):
        tmpl_g_rule = TemplateGroupRegexpRule(template_group["templates"])
        template_groups_rules[template_group["length"]] = tmpl_g_rule

    return template_groups_rules
