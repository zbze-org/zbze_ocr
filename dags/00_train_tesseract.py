import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from src.const import GLOBAL_TESSDATA_DIR, TESSTRAIN_LANG_CONFIG, TESSTRAIN_PROJECT_DIR

DAG_ID = "train_tesseract"

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
        "MODEL_NAME": "kbd_airflow",
        "START_MODEL": "rus",
        "MAX_ITERATIONS": "10000",
        "GROUND_TRUTH_DIR": "/Users/panagoa/tesstrain_data/60k_ng",
        "WORDLIST_FILE": os.path.join(TESSTRAIN_LANG_CONFIG, "kbd.numbers"),
        "NUMBERS_FILE": os.path.join(TESSTRAIN_LANG_CONFIG, "kbd.punc"),
        "PUNC_FILE": os.path.join(TESSTRAIN_LANG_CONFIG, "kbd.wordlist"),
        "LOG_FILE": "/Users/panagoa/PycharmProjects/tesstrain/plot/output_kbd_airflow.log",
        "TEST_PDF_NAME": "dysche_zhyg.pdf",
        "LANG_COMPARE": "kbd_0.009_4360_66700",
    },
)


def push_variables(**kwargs):
    model_name = kwargs["dag_run"].conf.get("MODEL_NAME")
    lang_compare = kwargs["dag_run"].conf.get("LANG_COMPARE")
    start_model = kwargs["dag_run"].conf.get("START_MODEL")
    max_iterations = kwargs["dag_run"].conf.get("MAX_ITERATIONS")
    ground_truth_dir = kwargs["dag_run"].conf.get("GROUND_TRUTH_DIR")
    wordlist_file = kwargs["dag_run"].conf.get("WORDLIST_FILE")
    numbers_file = kwargs["dag_run"].conf.get("NUMBERS_FILE")
    punc_file = kwargs["dag_run"].conf.get("PUNC_FILE")
    log_file = kwargs["dag_run"].conf.get("LOG_FILE")
    test_pdf_name = kwargs["dag_run"].conf.get("TEST_PDF_NAME")
    best_traineddata_dir = os.path.join(TESSTRAIN_PROJECT_DIR, "data", model_name, "tessdata_best")

    kwargs["ti"].xcom_push(key="MODEL_NAME", value=model_name)
    kwargs["ti"].xcom_push(key="START_MODEL", value=start_model)
    kwargs["ti"].xcom_push(key="MAX_ITERATIONS", value=max_iterations)
    kwargs["ti"].xcom_push(key="GROUND_TRUTH_DIR", value=ground_truth_dir)
    kwargs["ti"].xcom_push(key="WORDLIST_FILE", value=wordlist_file)
    kwargs["ti"].xcom_push(key="NUMBERS_FILE", value=numbers_file)
    kwargs["ti"].xcom_push(key="PUNC_FILE", value=punc_file)
    kwargs["ti"].xcom_push(key="LOG_FILE", value=log_file)
    kwargs["ti"].xcom_push(key="TEST_PDF_NAME", value=test_pdf_name)
    kwargs["ti"].xcom_push(key="LANG_COMPARE", value=lang_compare)

    kwargs["ti"].xcom_push(key="TESSTRAIN_DIR", value=TESSTRAIN_PROJECT_DIR)
    kwargs["ti"].xcom_push(key="BEST_TRAINEDDATA_DIR", value=best_traineddata_dir)
    kwargs["ti"].xcom_push(key="GLOBAL_TESSDATA_DIR", value=GLOBAL_TESSDATA_DIR)


t0_push_variables = PythonOperator(
    task_id="push_variables", python_callable=push_variables, provide_context=True, dag=dag
)

t1_run_train_tesseract = BashOperator(
    task_id="run_train_tesseract",
    cwd=TESSTRAIN_PROJECT_DIR,
    bash_command=(
        "nohup gmake training "
        "TESSDATA={{ ti.xcom_pull(key='GLOBAL_TESSDATA_DIR') }} "
        "MODEL_NAME={{ ti.xcom_pull(key='MODEL_NAME') }} "
        "START_MODEL={{ ti.xcom_pull(key='START_MODEL') }} "
        "MAX_ITERATIONS={{ ti.xcom_pull(key='MAX_ITERATIONS') }} "
        "GROUND_TRUTH_DIR={{ ti.xcom_pull(key='GROUND_TRUTH_DIR') }} "
        "WORDLIST_FILE={{ ti.xcom_pull(key='WORDLIST_FILE') }} "
        "NUMBERS_FILE={{ ti.xcom_pull(key='NUMBERS_FILE') }} "
        "PUNC_FILE={{ ti.xcom_pull(key='PUNC_FILE') }} "
        "| ts '[%Y-%m-%d %H:%M:%S]' | tee -a {{ ti.xcom_pull(key='LOG_FILE') }}"
    ),
    dag=dag,
)

t2_traineddata = BashOperator(
    task_id="traineddata",
    cwd=TESSTRAIN_PROJECT_DIR,
    bash_command=("nohup gmake traineddata " "MODEL_NAME={{ ti.xcom_pull(key='MODEL_NAME') }} "),
    dag=dag,
)

t3_cp_best_traineddata_to_tessdata = BashOperator(
    task_id="cp_best_traineddata_to_tessdata",
    cwd=TESSTRAIN_PROJECT_DIR,
    bash_command=(
        "BEST_TRAINEDDATA=$(ls {{ ti.xcom_pull(key='BEST_TRAINEDDATA_DIR') }} | grep traineddata | head -n 1) && "
        "cp {{ ti.xcom_pull(key='BEST_TRAINEDDATA_DIR') }}/$BEST_TRAINEDDATA "
        "data/{{ ti.xcom_pull(key='MODEL_NAME') }}.traineddata"
    ),
    dag=dag,
)

t4_cp_best_traineddata_to_global_tessdata = BashOperator(
    task_id="cp_best_traineddata_to_global_tessdata",
    cwd=TESSTRAIN_PROJECT_DIR,
    bash_command=(
        "BEST_TRAINEDDATA=$(ls {{ ti.xcom_pull(key='BEST_TRAINEDDATA_DIR') }} | grep traineddata | head -n 1) && "
        "cp {{ ti.xcom_pull(key='BEST_TRAINEDDATA_DIR') }}/$BEST_TRAINEDDATA "
        "{{ ti.xcom_pull(key='GLOBAL_TESSDATA_DIR') }}/$BEST_TRAINEDDATA"
    ),
    dag=dag,
)


def push_best_traineddata_to_xcom(**kwargs):
    best_traineddata_dir = kwargs["ti"].xcom_pull(key="BEST_TRAINEDDATA_DIR")
    best_traineddata_name = sorted(
        os.listdir(best_traineddata_dir),
        # key=lambda x: os.path.getmtime(os.path.join(best_traineddata_dir, x)),
    )[0]
    best_traineddata_name = best_traineddata_name.replace(".traineddata", "")
    kwargs["ti"].xcom_push(key="BEST_TRAINEDDATA_NAME", value=best_traineddata_name)


t5_push_best_traineddata_to_xcom = PythonOperator(
    task_id="push_best_traineddata_to_xcom",
    python_callable=push_best_traineddata_to_xcom,
    provide_context=True,
    dag=dag,
)

trigger = TriggerDagRunOperator(
    task_id="trigger_pdf_processing",
    trigger_dag_id="pdf_processing",
    conf={
        "TESSERACT_LANG": "{{ ti.xcom_pull(key='BEST_TRAINEDDATA_NAME') }}",
        "TESSERACT_LANG_COMPARE": "{{ ti.xcom_pull(key='LANG_COMPARE') }}",
        "PDF_NAME": "{{ ti.xcom_pull(key='TEST_PDF_NAME') }}",
    },
    dag=dag,
)

t0_push_variables >> t1_run_train_tesseract >> t2_traineddata
t2_traineddata >> t3_cp_best_traineddata_to_tessdata >> t4_cp_best_traineddata_to_global_tessdata
t4_cp_best_traineddata_to_global_tessdata >> t5_push_best_traineddata_to_xcom >> trigger
