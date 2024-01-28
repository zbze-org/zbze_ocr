import os
import re
from difflib import SequenceMatcher

import pandas as pd


def _get_text_by_lang(book_lang_txt_dir):
    lang_text_by_page = []
    for text_f in sorted(os.listdir(book_lang_txt_dir)):
        with open(os.path.join(book_lang_txt_dir, text_f)) as f:
            text = f.read()
            lang_text_by_page.append(text)

    return lang_text_by_page


def _extract_diff_words(line_1, line_2):
    line_1 = re.sub(r'[^\w\s]', '', line_1)
    line_2 = re.sub(r'[^\w\s]', '', line_2)

    words1 = line_1.split()
    words2 = line_2.split()

    sequence_matcher = SequenceMatcher(None, words1, words2)
    match = sequence_matcher.get_matching_blocks()

    different_words_1 = []
    different_words_2 = []

    start1 = 0
    start2 = 0

    for block in match:
        different_words_1.extend(words1[start1:block.a])
        different_words_2.extend(words2[start2:block.b])

        start1 = block.a + block.size
        start2 = block.b + block.size

    return tuple(different_words_1), tuple(different_words_2)


def _find_diff_words_by_lang(book_lang_1_txt_dir, book_lang_2_txt_dir):
    lang_1_text_by_page = _get_text_by_lang(book_lang_1_txt_dir)
    lang_2_text_by_page = _get_text_by_lang(book_lang_2_txt_dir)

    if len(lang_1_text_by_page) != len(lang_2_text_by_page):
        raise ValueError("Text lengths for both languages must be the same.")

    diff_words_1 = []
    diff_words_2 = []

    for page_i in range(len(lang_1_text_by_page)):
        page_text_1 = lang_1_text_by_page[page_i]
        page_text_2 = lang_2_text_by_page[page_i]

        for line_1, line_2 in zip(page_text_1.splitlines(), page_text_2.splitlines()):
            diff_w_1, diff_w_2 = _extract_diff_words(line_1, line_2)
            diff_words_1.append(diff_w_1)
            diff_words_2.append(diff_w_2)

    return diff_words_1, diff_words_2


def get_diff_word(book_lang_1_txt_dir, book_lang_2_txt_dir, lang_1, lang_2, output_file):
    diff_words_1, diff_words_2 = _find_diff_words_by_lang(
        book_lang_1_txt_dir=book_lang_1_txt_dir,
        book_lang_2_txt_dir=book_lang_2_txt_dir,
    )
    df = pd.DataFrame([{lang_1: ' '.join(w1), lang_2: ' '.join(w2)} for w1, w2 in zip(diff_words_1, diff_words_2)])
    df = df[df[lang_1] != ''][df[lang_2] != '']
    df.to_csv(output_file, index=False)
    return df
