from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from src import path_utils
from src.diff_by_langs import get_diff_word
from src.html_diff_by_langs import create_html_diff_by_lang
from src.lang_compare import compare_stats

DAG_ID = "compare_langs"

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(seconds=10),
}

dag = DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="An example DAG that mimics the Makefile logic",
    schedule_interval=None,
    params={
        "PDF_NAME": "dysche_zhyg.pdf",
        "LANG_1": "kbd_0.229_2995_10800",
        "LANG_2": "kbd_0.009_4360_66700",
    },
)


def push_variables(**kwargs):
    print(kwargs)
    PDF_NAME = kwargs["dag_run"].conf.get("PDF_NAME")
    LANG_1 = kwargs["dag_run"].conf.get("LANG_1")
    LANG_2 = kwargs["dag_run"].conf.get("LANG_2")

    book_base_dir = path_utils.get_book_base_dir(PDF_NAME)
    book_lang_1_dir = path_utils.get_book_lang_dir(book_base_dir, LANG_1)
    book_lang_2_dir = path_utils.get_book_lang_dir(book_base_dir, LANG_2)
    compare_results_dir = path_utils.get_compare_results_dir(book_base_dir, LANG_1, LANG_2)

    kwargs["ti"].xcom_push(key="PDF_NAME", value=PDF_NAME)
    kwargs["ti"].xcom_push(key="BOOK_BASE_DIR", value=book_base_dir)
    kwargs["ti"].xcom_push(key="COMPARE_RESULTS_DIR", value=compare_results_dir)
    kwargs["ti"].xcom_push(key="LANG_1", value=LANG_1)
    kwargs["ti"].xcom_push(key="LANG_2", value=LANG_2)
    kwargs["ti"].xcom_push(key="BOOK_LANG_1_DIR", value=book_lang_1_dir)
    kwargs["ti"].xcom_push(key="BOOK_LANG_2_DIR", value=book_lang_2_dir)


t0_push_variables = PythonOperator(
    task_id="push_variables", python_callable=push_variables, provide_context=True, dag=dag
)

t1_create_directories = BashOperator(
    task_id="create_directories",
    bash_command=("mkdir -p " '{{ti.xcom_pull(key="PDF_NAME")}} ' '{{ti.xcom_pull(key="COMPARE_RESULTS_DIR")}} '),
    dag=dag,
)


def run_compare_stats(**kwargs):
    compare_stats(
        book_base_dir=kwargs["ti"].xcom_pull(key="BOOK_BASE_DIR"),
        lang_1=kwargs["ti"].xcom_pull(key="LANG_1"),
        lang_2=kwargs["ti"].xcom_pull(key="LANG_2"),
        output_dir=kwargs["ti"].xcom_pull(key="COMPARE_RESULTS_DIR"),
    )


t2_tesseract_by_page = PythonOperator(
    task_id="compare_stats",
    python_callable=run_compare_stats,
    provide_context=True,
    dag=dag,
)


def run_make_html_diff(**kwargs):
    lang_1 = kwargs["ti"].xcom_pull(key="LANG_1")
    lang_2 = kwargs["ti"].xcom_pull(key="LANG_2")

    output_file = path_utils.get_html_diff_path(compare_results_dir=kwargs["ti"].xcom_pull(key="COMPARE_RESULTS_DIR"))
    create_html_diff_by_lang(
        book_base_dir=kwargs["ti"].xcom_pull(key="BOOK_BASE_DIR"),
        lang_1=lang_1,
        lang_2=lang_2,
        output_file=output_file,
    )


t3_make_html_diff = PythonOperator(
    task_id="make_html_diff",
    python_callable=run_make_html_diff,
    provide_context=True,
    dag=dag,
)


def extract_diff_words(**kwargs):
    book_base_dir = kwargs["ti"].xcom_pull(key="BOOK_BASE_DIR")
    lang_1 = kwargs["ti"].xcom_pull(key="LANG_1")
    lang_2 = kwargs["ti"].xcom_pull(key="LANG_2")

    book_lang_1_txt_dir = path_utils.get_book_lang_txt_dir(book_base_dir=book_base_dir, lang=lang_1)
    book_lang_2_txt_dir = path_utils.get_book_lang_txt_dir(book_base_dir=book_base_dir, lang=lang_2)
    compare_result_dir = path_utils.get_compare_results_dir(book_base_dir=book_base_dir, lang_1=lang_1, lang_2=lang_2)

    get_diff_word(
        book_lang_1_txt_dir=book_lang_1_txt_dir,
        book_lang_2_txt_dir=book_lang_2_txt_dir,
        lang_1=lang_1,
        lang_2=lang_2,
        output_file=path_utils.get_diff_words_path(compare_result_dir),
    )


t4_extract_diff_words = PythonOperator(
    task_id="extract_diff_words",
    python_callable=extract_diff_words,
    provide_context=True,
    dag=dag,
)

t0_push_variables >> t1_create_directories >> t2_tesseract_by_page >> t3_make_html_diff >> t4_extract_diff_words
