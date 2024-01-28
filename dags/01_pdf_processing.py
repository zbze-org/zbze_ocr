import os
from datetime import datetime, timedelta
from subprocess import Popen, PIPE

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from src.const import BASE_DAG_RESULTS_DIR, BASE_PDF_DIR, TESSERACT_CONFIG
from src.hocr_beatify import hocr_to_html

DAG_ID = 'pdf_processing'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(seconds=10),
}

dag = DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description='An example DAG that mimics the Makefile logic',
    schedule_interval=None,
    params={
        'TESSERACT_LANG': 'collected_3_from_oshamaho_new_font_0.193_4395_18400',
        'TESSERACT_LANG_COMPARE': 'kbd_ng',
        'PDF_NAME': 'dysche_zhyg.pdf',
    },
)


def push_variables(**kwargs):
    print(kwargs)
    tesseract_lang = kwargs['dag_run'].conf.get('TESSERACT_LANG')
    pdf_name = kwargs['dag_run'].conf.get('PDF_NAME')
    tesseract_lang_compare = kwargs['dag_run'].conf.get('TESSERACT_LANG_COMPARE')

    book_results_dir = os.path.join(BASE_DAG_RESULTS_DIR, DAG_ID, pdf_name)
    book_model_results_dir = os.path.join(book_results_dir, f'rslt_{tesseract_lang}')

    jpg_dir = os.path.join(book_model_results_dir, 'jpgs')
    txt_dir = os.path.join(book_model_results_dir, 'txts')
    hocr_dir = os.path.join(book_model_results_dir, 'hocrs')
    tsv_dir = os.path.join(book_model_results_dir, 'tsvs')
    pdf_file = os.path.join(BASE_PDF_DIR, pdf_name)

    kwargs['ti'].xcom_push(key='TESSERACT_LANG', value=tesseract_lang)
    kwargs['ti'].xcom_push(key='TESSERACT_LANG_COMPARE', value=tesseract_lang_compare)
    kwargs['ti'].xcom_push(key='PDF_NAME', value=pdf_name)
    kwargs['ti'].xcom_push(key='BOOK_MODEL_RESULTS_DIR', value=book_model_results_dir)
    kwargs['ti'].xcom_push(key='JPG_DIR', value=jpg_dir)
    kwargs['ti'].xcom_push(key='TXT_DIR', value=txt_dir)
    kwargs['ti'].xcom_push(key='HOCR_DIR', value=hocr_dir)
    kwargs['ti'].xcom_push(key='TSV_DIR', value=tsv_dir)
    kwargs['ti'].xcom_push(key='PDF_FILE', value=pdf_file)


t0_push_variables = PythonOperator(
    task_id='push_variables',
    python_callable=push_variables,
    provide_context=True,
    dag=dag
)

t1_create_directories = BashOperator(
    task_id='create_directories',
    bash_command=(
        'mkdir -p '
        '{{ti.xcom_pull(key="BOOK_MODEL_RESULTS_DIR")}} '
        '{{ti.xcom_pull(key="JPG_DIR")}} '
        '{{ti.xcom_pull(key="TXT_DIR")}} '
        '{{ti.xcom_pull(key="HOCR_DIR")}} '
        '{{ti.xcom_pull(key="TSV_DIR")}} '
    ),
    dag=dag,
)

t2_convert_pdf_to_jpg = BashOperator(
    task_id='convert_pdf_to_jpg',
    bash_command='pdftoppm -jpeg -r 300 {{ti.xcom_pull(key="PDF_FILE")}} {{ti.xcom_pull(key="JPG_DIR")}}/page',
    dag=dag,
)


def run_tesseract_for_page(**kwargs):
    tesseract_lang = kwargs['ti'].xcom_pull(key='TESSERACT_LANG')
    jpg_dir = kwargs['ti'].xcom_pull(key='JPG_DIR')
    txt_dir = kwargs['ti'].xcom_pull(key='TXT_DIR')
    print(f'tesseract_lang: {tesseract_lang} jpg_dir: {jpg_dir} txt_dir: {txt_dir}')

    jpgs = os.listdir(jpg_dir)
    print(f'jpgs: {jpgs}')

    for jpeg_file_name in jpgs:
        jpg_path = os.path.join(jpg_dir, jpeg_file_name)
        txt_path = os.path.join(txt_dir, jpeg_file_name.replace('.jpg', '.txt'))
        command = [
            'tesseract', '-l', tesseract_lang,
            jpg_path, txt_path, TESSERACT_CONFIG
        ]
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        print(f'output: {output} err: {err}')


t3_tesseract_by_page = PythonOperator(
    task_id='tesseract_by_page',
    python_callable=run_tesseract_for_page,
    provide_context=True,
    dag=dag,
)

t4_move_hocr_files = BashOperator(
    task_id='move_hocr_files',
    bash_command='mv {{ti.xcom_pull(key="TXT_DIR")}}/*.hocr {{ti.xcom_pull(key="HOCR_DIR")}}',
    dag=dag,
)

t5_move_tsv_files = BashOperator(
    task_id='move_tsv_files',
    bash_command='mv {{ti.xcom_pull(key="TXT_DIR")}}/*.tsv {{ti.xcom_pull(key="TSV_DIR")}}',
    dag=dag,
)


def join_page_hocr(**kwargs):
    hocr_dir = kwargs['ti'].xcom_pull(key='HOCR_DIR')
    output_path = os.path.join(hocr_dir, '..', 'output.html')
    hocr_to_html(hocr_dir, output_path)


t6_join_page_hocr = PythonOperator(
    task_id='join_page_hocr',
    python_callable=join_page_hocr,
    provide_context=True,
    dag=dag,
)

trigger = TriggerDagRunOperator(
    task_id='trigger_compare_langs',
    trigger_dag_id='compare_langs',
    conf={
        'PDF_NAME': '{{ ti.xcom_pull(key="PDF_NAME") }}',
        'LANG_1': "{{ ti.xcom_pull(key='TESSERACT_LANG_COMPARE') }}",
        'LANG_2': '{{ ti.xcom_pull(key="TESSERACT_LANG") }}',
    },
    dag=dag,
)

t0_push_variables >> t1_create_directories >> t2_convert_pdf_to_jpg >> t3_tesseract_by_page
t3_tesseract_by_page >> t4_move_hocr_files
t4_move_hocr_files >> t6_join_page_hocr
t3_tesseract_by_page >> t5_move_tsv_files >> trigger
