import os

from .const import PDF_PROCESSING_RESULT_DIR, TESSTRAIN_PROJECT_DIR


def get_book_base_dir(pdf_name):
    return os.path.join(PDF_PROCESSING_RESULT_DIR, pdf_name)


def get_book_lang_dir(book_base_dir, lang):
    return os.path.join(book_base_dir, f"rslt_{lang}")


def get_book_lang_txt_dir(book_base_dir, lang):
    return os.path.join(get_book_lang_dir(book_base_dir, lang), "txts")


def get_book_lang_tsv_dir(book_base_dir, lang):
    return os.path.join(get_book_lang_dir(book_base_dir, lang), "tsvs")


def get_best_traineddata_dir(model_name):
    return os.path.join(TESSTRAIN_PROJECT_DIR, "data", model_name, "tessdata_best")


def get_compare_results_dir(book_base_dir, lang_1, lang_2):
    return os.path.join(book_base_dir, f"cmpr_{lang_1}_vs_{lang_2}")


def get_diff_words_path(compare_results_dir):
    return os.path.join(compare_results_dir, "diff_words.csv")


def get_html_diff_path(compare_results_dir):
    return os.path.join(compare_results_dir, "merged_diff.html")
