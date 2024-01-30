NGRAM_TRESHOLDS = {
    2: [10, 100, 200, 500, 1000],
    3: [10, 50, 100, 200, 500],
    4: [10, 20, 30, 50, 100],
}


def get_ngram_tresholds_features(word, ngram_analyzer, ngrams_tresholds=None):
    ngrams = ngrams_tresholds or NGRAM_TRESHOLDS

    ngram_tresholds = {}

    for n, tresholds in ngrams.items():
        for treshold in tresholds:
            ngram_tresholds[f"{n}gram_treshold_{treshold}"] = ngram_analyzer.treshold_ngram(word, treshold, n=n)
            ngram_tresholds[f"{n}gram_treshold_m_{treshold}"] = ngram_analyzer.treshold_ngram_mean(word, treshold, n=n)

    return ngram_tresholds


def get_tokenizers_features(word, tokenizer_manager):
    tokenizers_features = {}
    for tokenizer_name, tokenizer in tokenizer_manager.tokenizers.items():
        tokenizer_features = _get_tokenizer_features(word, tokenizer, tokenizer_name)
        tokenizers_features.update(tokenizer_features)

    return tokenizers_features


def _get_tokenizer_features(word, tokenizer, tokenizer_name):
    tokenizer_features = {}

    tokens = tokenizer.encode(word).tokens
    token_ids = tokenizer.encode(word).ids

    tokenizer_features[f"{tokenizer_name}_char_count/token_count"] = len(word) / len(tokens)

    tokenizer_features[f"{tokenizer_name}_tokens"] = tokens
    tokenizer_features[f"{tokenizer_name}_tokens_count"] = len(tokens)
    tokenizer_features[f"{tokenizer_name}_token_ids"] = token_ids

    tokenizer_features[f"{tokenizer_name}_prefix"] = tokens[0]
    tokenizer_features[f"{tokenizer_name}_prefix_len"] = len(tokens[0])
    tokenizer_features[f"{tokenizer_name}_prefix_id"] = token_ids[0]

    tokenizer_features[f"{tokenizer_name}_suffix"] = tokens[-1]
    tokenizer_features[f"{tokenizer_name}_suffix_len"] = len(tokens[-1])
    tokenizer_features[f"{tokenizer_name}_suffix_id"] = token_ids[-1]

    return tokenizer_features


def get_word_trie_features(word, word_trie):
    word_trie_features = {}

    word_trie_features["longest_prefix"] = word_trie.get_longest_prefix(word)
    word_trie_features["longest_prefix_len"] = len(word_trie_features["longest_prefix"])
    word_trie_features["longest_prefix/word_len"] = len(word_trie_features["longest_prefix"]) / len(word)
    word_trie_features["longest_suffix"] = word_trie.get_longest_suffix(word)
    word_trie_features["longest_suffix_len"] = len(word_trie_features["longest_suffix"])
    word_trie_features["longest_suffix/word_len"] = len(word_trie_features["longest_suffix"]) / len(word)

    return word_trie_features


def fill_features(word, word_trie, ngram_analyzer, tokenizer_manager):
    features = {
        "word": word,
        "word_len": len(word),
    }

    tokenizers_features = get_tokenizers_features(word, tokenizer_manager)
    features.update(tokenizers_features)

    ngram_tresholds_features = get_ngram_tresholds_features(word, ngram_analyzer)
    features.update(ngram_tresholds_features)

    trie_features = get_word_trie_features(word, word_trie)
    features.update(trie_features)

    return features
