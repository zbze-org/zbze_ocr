import glob
import itertools
import os
from difflib import Differ, HtmlDiff

import click


@click.command()
@click.option("--directory", "-d", default=".", help="Directory path containing the files")
@click.option("--output-dir", "-o", default=None, help="Output directory path for the HTML file")
@click.option("--file-mask", "-m", default="*.txt", help="File mask for selecting files")
def compare_texts(directory, output_dir, file_mask):
    texts = []
    path = os.path.join(os.getcwd(), directory)
    file_pattern = os.path.join(path, file_mask)
    file_paths = glob.glob(file_pattern)

    for file_path in file_paths:
        with open(file_path) as f:
            text_i = f.read()
            texts.append((text_i, os.path.basename(file_path)))

    text_combi = list(itertools.combinations(texts, 2))

    d = Differ()
    html_diff = HtmlDiff()
    merged_text = ""
    different_words = []

    for (text_1, n1), (text_2, n2) in text_combi:
        diff = list(d.compare(text_1.split(), text_2.split()))
        for word_diff in diff:
            if word_diff.startswith("- ") or word_diff.startswith("+ "):
                word = word_diff[2:]
                different_words.append(word)

        merged_text += html_diff.make_file(
            fromlines=text_1.splitlines(keepends=True),
            tolines=text_2.splitlines(keepends=True),
            fromdesc=n1,
            todesc=n2,
            context=True,
        )
        merged_text += ""

    if output_dir is None:
        output_dir = directory

    output_path = os.path.join(os.getcwd(), output_dir)
    output_file = os.path.join(output_path, "merged_diff.html")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(merged_text)


if __name__ == "__main__":
    compare_texts()
