import os
import pickle
import re
from itertools import combinations

import pysnooper as pysnooper
from Levenshtein import distance
from django.conf import settings
from django.db.models.functions import Length
from tokenizers import Tokenizer

from ocr.models import OcrBoxText

with open(os.path.join(settings.BASE_DIR, 'ocr/src/aho_dawg.apkbr_ru.pkl'), 'rb') as f:
    # pip install pyahocorasick
    # import ahocorasick
    aho_dawg = pickle.load(f)


def is_word_exist_dawg(word):
    return aho_dawg.match(word)


def word_to_dawg_version(word):
    if aho_dawg.match(word):
        return word

    if aho_dawg.match(word.lower().replace('i', 'I')):
        return word.lower().replace('i', 'I')

    if aho_dawg.match(re.sub(r'[:.,!?]$', '', word)):
        return re.sub(r'[:.,!?]$', '', word)

    return word


def get_correction_candidates(word, tokenizer, max_spell=3):
    """Find potential correction candidates for a misspelled word."""
    tokens = tokenizer.encode(word).tokens

    candidates = dict()
    for token_combination in list(combinations(tokens, max_spell)):
        query_word = word
        for token in token_combination:
            query_word = query_word.replace(token, '?')

            candidates.update(aho_dawg.items(query_word, '?'))

    return candidates


@pysnooper.snoop(watch_explode=['suggestions'])
def get_suggestions(word_q, tokenizer, limit=10):
    suggestions = dict()
    suggestions.update(aho_dawg.items(f'{word_q}?', '?'))

    if len(suggestions) < limit:
        suggestions.update(aho_dawg.items(word_q))

    if len(suggestions) < limit:
        token_q = ''.join(tokenizer.encode(word_q).tokens[:-1])
        suggestions.update(aho_dawg.items(token_q))

    suggestions = {k: v for k, v in suggestions.items() if len(k) >= len(word_q)}
    suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)[:limit]
    return suggestions


def choose_best_candidate(word, candidates):
    """Select the best candidate for correction by calculating Levenshtein distance."""
    best_candidate = None
    best_distance = float('inf')

    for candidate, score in candidates.items():
        current_distance = distance(word, candidate)
        if current_distance < best_distance:
            best_candidate = candidate
            best_distance = current_distance

    return best_candidate, best_distance


class OcrWordService:

    def __init__(self):

        self.suggest_tokenizer = Tokenizer.from_file(
            os.path.join(settings.BASE_DIR, 'ocr/src/tokenizer_unigram_1000.json')
        )

        self.tokenizers_name_paths = [
            ('unigram_1k', os.path.join(settings.BASE_DIR, 'ocr/src/tokenizer_unigram_1000.json')),
            ('unigram_5k', os.path.join(settings.BASE_DIR, 'ocr/src/tokenizer_unigram_5000.json')),
            ('unigram_30k', os.path.join(settings.BASE_DIR, 'ocr/src/tokenizer_unigram_30000.json')),
            ('bpe_30k', os.path.join(settings.BASE_DIR, 'ocr/src/tokenizer_bpe_30000.json')),
        ]

        self.tokenizers = []
        for name, path in self.tokenizers_name_paths:
            tokenizer = Tokenizer.from_file(path)
            self.tokenizers.append((name, tokenizer))

    def get_word_frequency(self, word):
        frequency = aho_dawg.get(word, 0)
        return frequency

    def get_word_tokens(self, word):
        tokenizer_data = []

        for name, tokenizer in self.tokenizers:
            encoding = tokenizer.encode(word)

            tokens = encoding.tokens
            token_ids = encoding.ids
            tokens_count = len(tokens)

            word_token_data = {
                'morphemes': '-'.join(tokens),
                'tokens': tokens,
                'token_ids': token_ids,
                'tokens_count': tokens_count,
                'tokenizer': name,
            }
            tokenizer_data.append(word_token_data)

        return tokenizer_data

    def get_spell_errors(self, word):
        # TODO: Implement spell errors
        return [
            {'slug': 'error1', 'verbose': 'Verbose error 1'},
            {'slug': 'error2', 'verbose': 'Verbose error 2'}
        ]

    def get_error_spans(self, word):
        # TODO: Implement error spans
        return [
            {'start': 0, 'end': 5, 'error': 'error1'},
            {'start': 7, 'end': 10, 'error': 'error2'}
        ]

    def get_suggestions(self, word, limit=5):
        suggestions = []
        suggestions_i = get_suggestions(word, tokenizer=self.suggest_tokenizer, limit=limit)
        for candidate, freq in suggestions_i:
            suggestions.append(
                {
                    'word': candidate,
                    'frequency': freq,
                }
            )

        # suggestions = sorted(suggestions, key=lambda x: (-x['frequency']))
        return suggestions

    def get_correction_candidates(self, word, max_distance=3, max_candidates=10):
        correction_candidates_set = set()
        correction_candidates = []

        for name, tokenizer in self.tokenizers:
            correction_candidates_i = get_correction_candidates(word, tokenizer, max_spell=4)
            for candidate, freq in correction_candidates_i.items():
                dist = distance(word, candidate)
                if dist > max_distance:
                    continue

                if candidate in correction_candidates_set:
                    continue

                correction_candidates_set.add(candidate)
                correction_candidates.append(
                    {
                        'word': candidate,
                        'frequency': freq,
                        'distance': dist,
                        'score': freq / dist if dist > 0 else freq
                    }
                )

        correction_candidates = sorted(correction_candidates, key=lambda x: (-x['distance'], x['frequency']),
                                       reverse=True)
        return correction_candidates[:max_candidates]

    def get_image_info(self, word, ocr_page_id):
        box_text = OcrBoxText.objects.annotate(
            text_length=Length('text')
        ).filter(
            ocr_box_image__ocr_page_id=ocr_page_id,
            text__icontains=word,
        ).order_by('text_length').first()
        if not box_text:
            return {
                'image_link': None,
                'image_coords': None
            }

        box_image = box_text.ocr_box_image
        image_url = box_image.resized_image.url if box_image else None

        image_link = f'http://localhost:8000{image_url}'

        image_coords = [box_image.left, box_image.top, box_image.width, box_image.height] if box_image else None

        return {
            'confidence': box_text.confidence,
            'image_link': image_link,
            'image_coords': image_coords
        }

    def get_ocr_word_data(self, word, ocr_page_id):
        word = word_to_dawg_version(word)
        word_frequency = self.get_word_frequency(word)

        word_tokens = self.get_word_tokens(word)
        spell_errors = self.get_spell_errors(word)
        error_spans = self.get_error_spans(word)
        is_word_exist = is_word_exist_dawg(word)
        correction_candidates = self.get_correction_candidates(word)

        best_candidate = None
        if correction_candidates:
            best_candidate = correction_candidates[0]['word']

        image_info = self.get_image_info(word, ocr_page_id=ocr_page_id)

        data = {
            'word': word,
            'frequency': word_frequency,
            'word_tokens': word_tokens,
            'spell_errors': spell_errors,
            'error_spans': error_spans,
            'is_word_exist_dawg': is_word_exist,
            'correction_candidates': correction_candidates,
            'best_candidate': best_candidate,
            'image_link': image_info['image_link'],
            'image_coords': image_info['image_coords'],
            'confidence': image_info['confidence']
        }
        return data


ocr_word_service = OcrWordService()
