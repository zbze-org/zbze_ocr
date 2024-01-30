import gzip
import pickle
from collections import Counter

import pandas as pd
from tqdm import tqdm

from .defs import FEATURES_COLUMNS, MODEL_DATA_DIR, MODEL_PATH, WORD_FREQ_FILE_NAME
from .feature_filler import get_ngram_tresholds_features, get_tokenizers_features, get_word_trie_features
from .manager.ngram import NGramAnalyzer
from .manager.tokenization import TokenizerManager
from .manager.word_trie import WordTrie


class SpellCheckerService:
    def __init__(self, model_path, model_data_dir):
        self.model_path = model_path
        self.model_data_dir = model_data_dir
        self.model = None
        self.word_trie = None
        self.ngram_analyzer = None
        self.tokenizer_manager = None

    def load_model(self):
        with gzip.open(self.model_path, "rb") as f:
            self.model = pickle.load(f)

    def prepare_features_manager(self, word_freq_file_name):
        df = pd.read_csv(f"{self.model_data_dir}/{word_freq_file_name}", sep=",")
        trie_words = df[df["freq"] > 1]["word"].values.tolist()

        self.word_trie = WordTrie(words=trie_words)
        self.word_trie.make()
        self.ngram_analyzer = NGramAnalyzer(self.word_trie.get_words(), ngrams=(2, 3, 4))
        self.tokenizer_manager = TokenizerManager(
            tokenizer_paths={
                "unigram_5k": f"{self.model_data_dir}/words_unigram_5000.tokenizer.json",
                "bpe_5k": f"{self.model_data_dir}/bpe_5000.tokenizer.json",
            }
        )

    def fill_features(self, word):
        features = {
            "word": word,
            "word_len": len(word),
        }

        try:
            tokenizers_features = get_tokenizers_features(word, self.tokenizer_manager)
            features.update(tokenizers_features)
        except ZeroDivisionError:
            pass

        try:
            ngram_tresholds_features = get_ngram_tresholds_features(word, self.ngram_analyzer)
            features.update(ngram_tresholds_features)
        except ZeroDivisionError:
            pass

        try:
            trie_features = get_word_trie_features(word, self.word_trie)
            features.update(trie_features)
        except ZeroDivisionError:
            pass

        return features

    def predict(self, words, return_df=False, verbose=False):
        cnt = Counter(words)
        uniq_words = cnt.keys()

        features_data = [self.fill_features(word) for word in tqdm(uniq_words)]
        features_df = pd.DataFrame(features_data)

        to_predict_df = features_df[FEATURES_COLUMNS].dropna()
        calculated_df = pd.DataFrame()
        calculated_df["calc"] = self.model.predict(to_predict_df)

        result_df = features_df.merge(calculated_df, left_index=True, right_index=True, how="left")
        result_df["freq"] = result_df["word"].apply(lambda x: cnt[x])
        result_df.fillna(0, inplace=True)

        if not verbose:
            result_df = result_df[["word", "calc", "freq"]]

        if return_df is False and verbose is False:
            return dict(zip(result_df["word"], result_df["calc"]))
        elif return_df is False and verbose is True:
            return result_df.to_dict("records")
        else:
            return result_df


def create_spell_checker_service(
    model_path=MODEL_PATH, model_dir=MODEL_DATA_DIR, word_freq_file_name=WORD_FREQ_FILE_NAME
):
    spell_checker_service = SpellCheckerService(
        model_path=model_path,
        model_data_dir=model_dir,
    )
    spell_checker_service.load_model()
    spell_checker_service.prepare_features_manager(word_freq_file_name=word_freq_file_name)
    return spell_checker_service
