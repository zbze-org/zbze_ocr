import csv
import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from . import path_utils

matplotlib.use("Agg")


def get_book_df(book_lang_tsv_dir):
    book_df = pd.DataFrame()
    for filename in sorted(os.listdir(book_lang_tsv_dir)):
        if filename.endswith('.tsv'):
            try:
                page_df = pd.read_csv(
                    os.path.join(book_lang_tsv_dir, filename),
                    sep='\t',
                    header=0,
                    quoting=csv.QUOTE_NONE,
                )
            except pd.errors.ParserError as e:
                print(f'Error while parsing {book_lang_tsv_dir} {filename}: {e}')
                raise
            page_df['page'] = filename.split('.')[0]
            book_df = pd.concat([book_df, page_df], ignore_index=True)
    return book_df


def _plot_conf_dist(book_df, lang, output_dir, conf_min=0, conf_max=100):
    plt.figure(figsize=(10, 6))
    sns.histplot(book_df['conf'][book_df['conf'] >= conf_min][book_df['conf'] <= conf_max], bins=20)
    plt.title(f'Гистограмма уровней уверенности ({lang})')
    plt.xlabel('Уровень уверенности')
    plt.ylabel('Количество')
    # plt.show()
    plt.savefig(os.path.join(output_dir, f'conf_dist_{lang}_{conf_min}_{conf_max}.png'))


def _plot_filtered_conf_dist_by_page(filtered_df, lang, output_dir, conf_min=0, conf_max=100):
    plt.figure(figsize=(30, 10))
    sns.histplot(filtered_df['page'], bins=len(filtered_df['page'].unique()))
    plt.title(f'Количество строк с уровнем уверенности < {conf_max} ({lang})')
    plt.xlabel('Номер страницы')
    plt.ylabel('Количество')
    plt.xticks(rotation=90)
    # plt.show()
    plt.savefig(os.path.join(output_dir, f'filtered_conf_dist_by_page_{lang}_{conf_min}_{conf_max}.png'))


def _filter_by_conf(book_df, lang, output_dir, conf_min=0, conf_max=100):
    filtered_df = book_df[book_df['conf'] >= conf_min][book_df['conf'] <= conf_max]
    _plot_filtered_conf_dist_by_page(filtered_df, lang, output_dir, conf_max=conf_max)
    filtered_df.to_csv(os.path.join(output_dir, f'filtered_{conf_min}_{conf_max}_book_df_{lang}.tsv'), sep='\t')


def compare_stats(book_base_dir, lang_1, lang_2, output_dir, conf_threshold=90):
    book_lang_1_tsv_dir = path_utils.get_book_lang_tsv_dir(book_base_dir, lang_1)
    book_lang_2_tsv_dir = path_utils.get_book_lang_tsv_dir(book_base_dir, lang_2)

    book_df_1 = get_book_df(book_lang_tsv_dir=book_lang_1_tsv_dir)
    book_df_2 = get_book_df(book_lang_tsv_dir=book_lang_2_tsv_dir)

    book_df_1 = book_df_1.dropna()
    book_df_2 = book_df_2.dropna()
    _plot_conf_dist(book_df_1, lang_1, output_dir, conf_max=90)
    _plot_conf_dist(book_df_2, lang_2, output_dir, conf_max=90)

    book_df_1.to_csv(os.path.join(output_dir, f'book_df_{lang_1}.tsv'), sep='\t')
    book_df_2.to_csv(os.path.join(output_dir, f'book_df_{lang_2}.tsv'), sep='\t')

    book_df_1.describe().to_csv(os.path.join(output_dir, f'book_df_{lang_1}_describe.tsv'), sep='\t')
    book_df_2.describe().to_csv(os.path.join(output_dir, f'book_df_{lang_2}_describe.tsv'), sep='\t')

    join_by = ['page', 'text', 'level', 'page_num', 'block_num', 'par_num', 'line_num']
    inner_df = pd.merge(book_df_1, book_df_2, on=join_by, suffixes=('_1', '_2'))

    inner_show_cols = ['text', 'conf_1', 'conf_2']
    inner_df = inner_df[inner_show_cols]
    inner_df.to_csv(os.path.join(output_dir, f'inner_df.tsv'), sep='\t')

    left_show_cols = ['page', 'text', 'conf_1', 'conf_2']
    left_df = pd.merge(book_df_1, book_df_2, on=join_by, how='left', suffixes=('_1', '_2'))
    left_df = left_df[left_df['conf_2'].isna()]
    left_df = left_df[left_show_cols]
    left_df.to_csv(os.path.join(output_dir, f'left_{lang_1}_df.tsv'), sep='\t')

    right_show_cols = ['page', 'text', 'conf_1', 'conf_2']
    right_df = pd.merge(book_df_1, book_df_2, on=join_by, how='right', suffixes=('_1', '_2'))
    right_df = right_df[right_df['conf_1'].isna()]
    right_df = right_df[right_show_cols]
    right_df.to_csv(os.path.join(output_dir, f'right_{lang_2}_df.tsv'), sep='\t')

    # filter by conf
    for max_conf in [30, 60, 90]:
        _filter_by_conf(book_df_1, lang_1, output_dir, conf_max=max_conf)
        _filter_by_conf(book_df_2, lang_2, output_dir, conf_max=max_conf)


if __name__ == '__main__':
    _book_base_dir = '../data/dag_results/pdf_processing/dysche_zhyg.pdf'
    _lang_1 = 'kbd_0.009_4360_66700'
    _lang_2 = 'kbd_0.229_2995_10800'
    _output_dir = os.path.join(_book_base_dir, f'compare_{_lang_1}_vs_{_lang_2}')
    compare_stats(_book_base_dir, _lang_1, _lang_2, output_dir=_output_dir)
