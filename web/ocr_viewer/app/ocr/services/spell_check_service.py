import json
import os
import pickle
import re
from enum import Enum

from tokenizers import Tokenizer

from ocr.services.word_service import is_word_exist_dawg
from setting import settings

MIN_CHARACTER_COMBINATIONS_FREQUENCY = 200
MIN_WORD_LENGTH = 3

tokenizer = Tokenizer.from_file(
    os.path.join(settings.BASE_DIR, 'ocr/src/tokenizer_unigram_30000.json')
)

with open(os.path.join(settings.BASE_DIR, 'ocr/src/prefixes_dawg.pkl'), 'rb') as f:
    prefixes_dawg = pickle.load(f)

with open(os.path.join(settings.BASE_DIR, 'ocr/src/suffixes_dawg.pkl'), 'rb') as f:
    suffixes_dawg = pickle.load(f)

combinations = json.load(open(os.path.join(settings.BASE_DIR, 'ocr/src/ch_bigram.json')))
combinations = sorted(combinations, key=lambda x: x[1])
combinations = [ch for ch, freq in combinations if freq < MIN_CHARACTER_COMBINATIONS_FREQUENCY]


def has_digits(word):
    return any(char.isdigit() for char in word)


def has_uppercase_in_the_middle(word):
    return any(char.isupper() for char in word[1:-1] if char not in ['I'])


def has_consecutive_duplicates(word):
    return any(char1 == char2 for char1, char2 in zip(word, word[1:]))


def is_too_short(word):
    return len(word) <= MIN_WORD_LENGTH


def has_one_char_token(word, limit=1):
    return [len(token) for token in tokenizer.encode(word).tokens].count(1) > limit


def starts_with_forbidden_letters(word):
    forbidden_letters = ['ы', 'ъ', 'ь', 'нц']
    return any(word.startswith(letter) for letter in forbidden_letters)


def endswith_with_forbidden_letters(word):
    forbidden_letters = ['рн', ]
    return any(word.endswith(letter) for letter in forbidden_letters)


def has_forbidden_letter_combination(word):
    for chars in combinations:
        if chars in word:
            return True


def prefix_not_in_dawg(word):
    if len(word) <= 3:
        return False

    for i in range(len(word), 2, -1):
        if prefixes_dawg.match(word[:i]):
            return False
    return True


def suffix_not_in_dawg(word):
    if len(word) <= 3:
        return False

    for i in range(len(word), 2, -1):
        if suffixes_dawg.match(word[-i:]):
            return False
    return True


def word_not_in_dawg(word):
    return not is_word_exist_dawg(word)


class Severity(Enum):
    Ignore = 0
    Info = 1
    Warning = 2
    Error = 3


class SpellCheckService:
    def __init__(self):
        self.validators = [
            (word_not_in_dawg, 'слово не найдено в словаре', Severity.Error.value),
            (starts_with_forbidden_letters, 'слово начинается с запрещенной буквы', Severity.Error.value),
            (endswith_with_forbidden_letters, 'слово заканчивается запрещенной буквой', Severity.Error.value),
            (has_uppercase_in_the_middle, 'заглавная буква в середине слова', Severity.Error.value),
            (has_digits, 'цифра в слове', Severity.Error.value),
            (has_forbidden_letter_combination, 'непопулярное сочетание букв', Severity.Warning.value),
            (has_consecutive_duplicates, 'две буквы идут подряд', Severity.Warning.value),
            (prefix_not_in_dawg, 'неизвестный префикс', Severity.Warning.value),
            (suffix_not_in_dawg, 'неизвестный суффикс', Severity.Warning.value),
            (is_too_short, 'слишком короткое слово', Severity.Warning.value),
            (has_one_char_token, 'однобуквенный токен', Severity.Warning.value),
        ]

    @staticmethod
    def text_to_ranges(text):
        text_ranges = []
        lines = text.split('\n')
        for line_number, line_content in enumerate(lines, start=1):
            word_matches = re.findall(r'\w+', line_content, re.UNICODE)
            for match in word_matches:
                word = match.strip()
                text_ranges.append((
                    (
                        line_number,
                        line_number,
                        line_content.index(match) + 1,  # +1 because Monaco editor is 1-based
                        line_content.index(match) + len(match) + 1,  # +1 because Monaco editor is 1-based
                    ), word
                ))
        return text_ranges

    def check(self, text):
        markers = []

        ranges = self.text_to_ranges(text)
        for (sl, el, sc, ec), word in ranges:
            for validator, message, severity in self.validators:
                if validator(word):
                    markers.append({
                        'word': word,
                        'message': message,
                        'severity': severity,
                        'startLineNumber': sl,
                        'endLineNumber': el,
                        'startColumn': sc,
                        'endColumn': ec,
                    })
                    break

        return markers
