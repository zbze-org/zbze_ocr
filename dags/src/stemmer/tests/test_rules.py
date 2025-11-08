import unittest

from parameterized import parameterized

from ..rules.base import BaseRule, create_template_group_rule, min_length_condition
from ..stemmer import Stemmer


class TestRule1(unittest.TestCase):
    @parameterized.expand(
        [
            ("ахэри", "ахэри", False),
            ("шхэри", "шхэри", False),
            ("Iуащхьэхэри", "Iуащхьэ", True),
            ("Iувхэри", "Iув", True),
        ]
    )
    def test_rule_6(self, word, expected, is_applicable=True):
        rule = BaseRule(
            pattern="хэри$",
            conditions=[
                lambda x: min_length_condition(x, min_length=6),
            ],
        )
        self.assertEqual(rule.is_applicable(word), is_applicable)
        word, applied = rule.apply(word)
        self.assertEqual(word, expected)

    @parameterized.expand(
        [
            ("шхэри", "шхэ", True),
            ("сэри", "сэ", True),
            ("ахэри", "ахэри", False),
            ("ари", "ари", False),
        ]
    )
    def test_rule_4(self, word, expected, is_applicable=True):
        rule = BaseRule(
            pattern="ри$",
            conditions=[
                lambda x: min_length_condition(x, min_length=4),
            ],
            excluded_words=["ахэри"],
        )
        self.assertEqual(rule.is_applicable(word), is_applicable)
        word, applied = rule.apply(word)
        self.assertEqual(word, expected)

    @parameterized.expand(
        [
            ("ахэри", "ахэр", True),
            ("ари", "ар", True),
        ]
    )
    def test_rule_3(self, word, expected, is_applicable=True):
        rule = BaseRule(
            pattern="и$",
            conditions=[
                lambda x: min_length_condition(x, min_length=3),
            ],
        )
        self.assertEqual(rule.is_applicable(word), is_applicable)
        word, applied = rule.apply(word)
        self.assertEqual(word, expected)


class TestStemmer(unittest.TestCase):
    def setUp(self):
        group_rules = create_template_group_rule("/dags/src/stemmer/tests/data/template_groups_by_len.json")
        self.stemmer = Stemmer(
            rules=[rule for g, rule in sorted(group_rules.items(), key=lambda x: x[0], reverse=True)]
        )

    @parameterized.expand(
        [
            ("Iуащхьэхэри", "Iуащхь"),
            ("Iувхэри", "Iув"),
            ("шхэри", "шхэ"),
            ("яхузэфIэмыкIын", "фIэмыкIын"),
            ("хузэфIэмыкIынкIэ", "фIэмыкIын"),
        ]
    )
    def test_apply(self, word, expected):
        self.assertEqual(self.stemmer.stem(word), expected)

    @parameterized.expand(
        [
            ("Iуащхьэхэри", []),
            ("Iувхэри", []),
            ("шхэри", []),
            ("яхузэфIэмыкIын", []),
            ("хузэфIэмыкIынкIэ", []),
            ("гъэунэхуныгъэшхуэри", []),
            ("гъэунэхуныгъэ", []),
            ("къэралыгъуэшхуэщи", []),
            ("къэралыгъуэшхуэ", []),
            ("гущIэгъуншагъэрэ", []),
        ]
    )
    def test_find_possible_stems(self, word, expected):
        self.assertEqual(self.stemmer.find_possible_stems(word), expected)
