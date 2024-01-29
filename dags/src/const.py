import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TESSERACT_CONFIG_DIR = os.path.join(PROJECT_DIR, 'tesseract')
TESSERACT_CONFIG = os.path.join(TESSERACT_CONFIG_DIR, 'kdb.base.config.txt')
TESSTRAIN_LANG_CONFIG = os.path.join(TESSERACT_CONFIG_DIR, 'tesstrain/kbd/configs')
BASE_DATA_DIR = os.path.join(PROJECT_DIR, 'data')
BASE_DAG_RESULTS_DIR = os.path.join(BASE_DATA_DIR, 'dag_results')
BASE_PDF_DIR = os.path.join(BASE_DATA_DIR, 'pdfs')
PDF_PROCESSING_RESULT_DIR = os.path.join(BASE_DAG_RESULTS_DIR, 'pdf_processing')
LANG_COMPARE_RESULT_DIR = os.path.join(BASE_DAG_RESULTS_DIR, 'lang_compare')

TESSTRAIN_PROJECT_DIR = '/Users/panagoa/PycharmProjects/tesstrain'
TESSTRAIN_TESSDATA_DIR = os.path.join(TESSTRAIN_PROJECT_DIR, 'usr/share/tessdata')
GLOBAL_TESSDATA_DIR = '/opt/homebrew/share/tessdata'

FONT_DIR = '../fonts'
FONT_SIZE = 20
TEXT_LINES_MAX_COUNT = 1000000

SPELLCHECKER_DIR = os.path.join(PROJECT_DIR, 'dags', 'src', 'spellcheck')
