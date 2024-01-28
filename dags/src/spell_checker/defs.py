import os

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(ABS_PATH, 'models')
MODEL_DATA_DIR = os.path.join(MODEL_DIR, 'data')
MODEL_NAME = 'rf_classifier_model_freq_1000000_oshhamaho.txt.pkl.gz'
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)
WORD_FREQ_FILE_NAME = 'word_freq_1000000_oshhamaho.csv'

FEATURES_COLUMNS = [
    'word_len',
    'unigram_5k_char_count/token_count',
    'unigram_5k_tokens_count',
    'unigram_5k_prefix_len',
    'unigram_5k_suffix_len',
    'bpe_5k_char_count/token_count',
    'bpe_5k_tokens_count',
    'bpe_5k_prefix_len',
    'bpe_5k_suffix_len',

    '2gram_treshold_10',
    '2gram_treshold_m_10',
    '2gram_treshold_100',
    '2gram_treshold_m_100',
    '2gram_treshold_200',
    '2gram_treshold_m_200',
    '2gram_treshold_500',
    '2gram_treshold_m_500',
    '2gram_treshold_1000',
    '2gram_treshold_m_1000',

    '3gram_treshold_10',
    '3gram_treshold_m_10',
    '3gram_treshold_50',
    '3gram_treshold_m_50',
    '3gram_treshold_100',
    '3gram_treshold_m_100',
    '3gram_treshold_200',
    '3gram_treshold_m_200',
    '3gram_treshold_500',
    '3gram_treshold_m_500',

    '4gram_treshold_10',
    '4gram_treshold_m_10',
    '4gram_treshold_20',
    '4gram_treshold_m_20',
    '4gram_treshold_30',
    '4gram_treshold_m_30',
    '4gram_treshold_50',
    '4gram_treshold_m_50',
    '4gram_treshold_100',
    '4gram_treshold_m_100',

    'longest_prefix_len',
    'longest_prefix/word_len',
    'longest_suffix_len',
    'longest_suffix/word_len',
]
