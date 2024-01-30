from tokenizers import Tokenizer


class TokenizerManager:
    def __init__(self, tokenizer_paths):
        self.tokenizers = {name: Tokenizer.from_file(path) for name, path in tokenizer_paths.items()}

    def get_tokenizer(self, tokenizer_name):
        return self.tokenizers.get(tokenizer_name)

    def tokenize(self, word, tokenizer_name):
        tokenizer = self.get_tokenizer(tokenizer_name)
        return tokenizer.encode(word) if tokenizer else None


def char_len_tokens(word, tokenizer):
    toke_len_hash = "".join([str(len(token)) for token in tokenizer.encode(word).tokens])
    return toke_len_hash


def has_one_char_token_consecutively(word, tokenizer):
    return "11" in char_len_tokens(word, tokenizer)


def has_many_one_char_tokens(word, tokenizer, n=1):
    return char_len_tokens(word, tokenizer).count("1") >= n


def token_ids(word, tokenizer):
    return tokenizer.encode(word).ids
