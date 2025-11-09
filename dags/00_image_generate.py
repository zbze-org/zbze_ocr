import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from src.const import TESSTRAIN_PROJECT_DIR
from src.image_generator import generate_images
from src.prepare_tessdata import prepare_box_lstmf

DAG_ID = "image_generate"

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(seconds=10),
}

dag = DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="Images generation for tesseract training",
    schedule_interval=None,
    params={
        "TEXT_FILEPATH": "data/tesstrain/kbd/data/output/lines_oshamaho.txt",
        "FONT_DIR": "data/tesstrain/kbd/fonts",
        "OUTPUT_DIR": os.getenv("TESSTRAIN_DATA_DIR", os.path.join(TESSTRAIN_PROJECT_DIR, "data")),
        "FONT_SIZE": 20,
        "TEXT_LINES_MAX_COUNT": 5000,
        "GROUP_BY": 0,
        "GROUP_BY_FACTOR": 0,
        "PAR_FACTOR": 4,
        "TESSTRAIN_MODEL_NAME": "",
        "TESSTRAIN_START_MODEL": "rus",
        "TESSTRAIN_MAX_ITERATIONS": "20000",
        "TESSTRAIN_GROUND_TRUTH_DIR": os.getenv("GROUND_TRUTH_DIR", os.path.join(TESSTRAIN_PROJECT_DIR, "data/ground_truth")),
        "TESSTRAIN_WORDLIST_FILE": "data/tesstrain/kbd/configs/kbd.numbers",
        "TESSTRAIN_NUMBERS_FILE": "data/tesstrain/kbd/configs/kbd.punc",
        "TESSTRAIN_PUNC_FILE": "data/tesstrain/kbd/configs/kbd.wordlist",
        "TESSTRAIN_LOG_FILE": os.getenv("TESSTRAIN_LOG_FILE", os.path.join(TESSTRAIN_PROJECT_DIR, "plot/output_kbd_airflow.log")),
        "TESSTRAIN_TEST_PDF_NAME": "dysche_zhyg.pdf",
        "TESSTRAIN_LANG_COMPARE": "kbd_0.009_4360_66700",
    },
)


def push_variables(**kwargs):
    text_filepath = kwargs["dag_run"].conf.get("TEXT_FILEPATH")
    font_dir = kwargs["dag_run"].conf.get("FONT_DIR")
    output_dir = kwargs["dag_run"].conf.get("OUTPUT_DIR")
    font_size = kwargs["dag_run"].conf.get("FONT_SIZE")
    max_lines = kwargs["dag_run"].conf.get("TEXT_LINES_MAX_COUNT")
    group_by = kwargs["dag_run"].conf.get("GROUP_BY")
    group_by_factor = kwargs["dag_run"].conf.get("GROUP_BY_FACTOR")
    par_factor = kwargs["dag_run"].conf.get("PAR_FACTOR")

    # ground_truth_dir = kwargs['dag_run'].conf.get('TESSTRAIN_GROUND_TRUTH_DIR')
    ground_truth_dir = output_dir
    start_model = kwargs["dag_run"].conf.get("TESSTRAIN_START_MODEL")
    max_iterations = kwargs["dag_run"].conf.get("TESSTRAIN_MAX_ITERATIONS")
    wordlist_file = kwargs["dag_run"].conf.get("TESSTRAIN_WORDLIST_FILE")
    numbers_file = kwargs["dag_run"].conf.get("TESSTRAIN_NUMBERS_FILE")
    punc_file = kwargs["dag_run"].conf.get("TESSTRAIN_PUNC_FILE")
    log_file = kwargs["dag_run"].conf.get("TESSTRAIN_LOG_FILE")
    test_pdf_name = kwargs["dag_run"].conf.get("TESSTRAIN_TEST_PDF_NAME")
    lang_compare = kwargs["dag_run"].conf.get("TESSTRAIN_LANG_COMPARE")

    model_name = kwargs["dag_run"].conf.get("TESSTRAIN_MODEL_NAME")
    if not model_name:
        text_filename = os.path.basename(text_filepath).split(".")[0]
        max_lines_str = str(max_lines)

        model_name = f"{text_filename}_{max_lines_str}"

    kwargs["ti"].xcom_push(key="MODEL_NAME", value=model_name)

    kwargs["ti"].xcom_push(key="TEXT_FILEPATH", value=text_filepath)
    kwargs["ti"].xcom_push(key="FONT_DIR", value=font_dir)
    kwargs["ti"].xcom_push(key="OUTPUT_DIR", value=output_dir)
    kwargs["ti"].xcom_push(key="FONT_SIZE", value=font_size)
    kwargs["ti"].xcom_push(key="TEXT_LINES_MAX_COUNT", value=max_lines)
    kwargs["ti"].xcom_push(key="GROUP_BY", value=group_by)
    kwargs["ti"].xcom_push(key="GROUP_BY_FACTOR", value=group_by_factor)
    kwargs["ti"].xcom_push(key="PAR_FACTOR", value=par_factor)

    kwargs["ti"].xcom_push(key="START_MODEL", value=start_model)
    kwargs["ti"].xcom_push(key="MAX_ITERATIONS", value=max_iterations)
    kwargs["ti"].xcom_push(key="GROUND_TRUTH_DIR", value=ground_truth_dir)
    kwargs["ti"].xcom_push(key="WORDLIST_FILE", value=wordlist_file)
    kwargs["ti"].xcom_push(key="NUMBERS_FILE", value=numbers_file)
    kwargs["ti"].xcom_push(key="PUNC_FILE", value=punc_file)
    kwargs["ti"].xcom_push(key="LOG_FILE", value=log_file)
    kwargs["ti"].xcom_push(key="TEST_PDF_NAME", value=test_pdf_name)
    kwargs["ti"].xcom_push(key="LANG_COMPARE", value=lang_compare)


t0_push_variables = PythonOperator(
    task_id="push_variables", python_callable=push_variables, provide_context=True, dag=dag
)


def run_image_generate(**kwargs):
    text_filepath = kwargs["ti"].xcom_pull(key="TEXT_FILEPATH")
    font_dir = kwargs["ti"].xcom_pull(key="FONT_DIR")
    output_dir = kwargs["ti"].xcom_pull(key="OUTPUT_DIR")
    font_size = kwargs["ti"].xcom_pull(key="FONT_SIZE")
    max_lines = kwargs["ti"].xcom_pull(key="TEXT_LINES_MAX_COUNT")
    group_by = kwargs["ti"].xcom_pull(key="GROUP_BY")
    group_by_factor = kwargs["ti"].xcom_pull(key="GROUP_BY_FACTOR")
    par_factor = kwargs["ti"].xcom_pull(key="PAR_FACTOR")

    subdirs = generate_images(
        text_filepath=text_filepath,
        font_dir=font_dir,
        output_dir=output_dir,
        font_size=font_size,
        max_lines=max_lines,
        group_by=group_by,
        group_by_factor=group_by_factor,
        par_factor=par_factor,
    )
    kwargs["ti"].xcom_push(key="SUBDIRS", value=subdirs)


t1_image_generate = PythonOperator(
    task_id="image_generate", python_callable=run_image_generate, provide_context=True, dag=dag
)


def run_prepare_tessdata(**kwargs):
    ground_truth_dir = kwargs["ti"].xcom_pull(key="GROUND_TRUTH_DIR")
    par_factor = kwargs["ti"].xcom_pull(key="PAR_FACTOR")

    prepare_box_lstmf(
        ground_truth_dir=ground_truth_dir,
        walk_subdirs=False,
        par_factor=par_factor,
    )


t2_prepare_tessdata = PythonOperator(
    task_id="prepare_tessdata", python_callable=run_prepare_tessdata, provide_context=True, dag=dag
)

trigger = TriggerDagRunOperator(
    task_id="trigger_pdf_processing",
    trigger_dag_id="train_tesseract",
    conf={
        "MODEL_NAME": "{{ ti.xcom_pull(key='MODEL_NAME') }}",
        "START_MODEL": "{{ ti.xcom_pull(key='START_MODEL') }}",
        "MAX_ITERATIONS": "{{ ti.xcom_pull(key='MAX_ITERATIONS') }}",
        "GROUND_TRUTH_DIR": "{{ ti.xcom_pull(key='GROUND_TRUTH_DIR') }}",
        "WORDLIST_FILE": "{{ ti.xcom_pull(key='WORDLIST_FILE') }}",
        "NUMBERS_FILE": "{{ ti.xcom_pull(key='NUMBERS_FILE') }}",
        "PUNC_FILE": "{{ ti.xcom_pull(key='PUNC_FILE') }}",
        "LOG_FILE": "{{ ti.xcom_pull(key='LOG_FILE') }}",
        "TEST_PDF_NAME": "{{ ti.xcom_pull(key='TEST_PDF_NAME') }}",
        "LANG_COMPARE": "{{ ti.xcom_pull(key='LANG_COMPARE') }}",
    },
    dag=dag,
)

t0_push_variables >> t1_image_generate >> t2_prepare_tessdata >> trigger
