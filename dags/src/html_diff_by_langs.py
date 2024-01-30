import os
from difflib import HtmlDiff


def _get_text_by_lang(book_lang_txt_dir):
    lang_text_by_page = []
    for text_f in sorted(os.listdir(book_lang_txt_dir)):
        with open(os.path.join(book_lang_txt_dir, text_f)) as f:
            text = f.read()
            lang_text_by_page.append(text)

    return lang_text_by_page


def create_html_diff_by_lang(book_base_dir, lang_1, lang_2, output_file):
    html_diff = HtmlDiff()

    lang_1_text_by_page = _get_text_by_lang(book_lang_txt_dir=os.path.join(book_base_dir, f"rslt_{lang_1}", "txts"))
    lang_2_text_by_page = _get_text_by_lang(book_lang_txt_dir=os.path.join(book_base_dir, f"rslt_{lang_2}", "txts"))

    merged_text = ""
    for page_i in range(len(lang_2_text_by_page)):
        diff = html_diff.make_file(
            fromlines=lang_1_text_by_page[page_i].splitlines(keepends=True),
            tolines=lang_2_text_by_page[page_i].splitlines(keepends=True),
            fromdesc=f"page:{page_i} ({lang_1})",
            todesc=f"page:{page_i} ({lang_1})",
            context=True,
        )
        merged_text += diff

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(merged_text)


if __name__ == "__main__":
    _book_base_dir = "../data/dag_results/pdf_processing/dysche_zhyg.pdf"
    _lang_1 = "kbd_0.229_2995_10800"
    _lang_2 = "kbd_0.009_4360_66700"
    _output_file = os.path.join(_book_base_dir, f"merged_diff_{_lang_1}_vs_{_lang_2}.html")
    create_html_diff_by_lang(_book_base_dir, _lang_1, _lang_2, _output_file)
