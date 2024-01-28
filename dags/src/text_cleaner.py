import re

NOT_IN_WHITELIST_REGEX = r"[^АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯяIi1\-\.\,\:\; \
-!?–…«»1234567890)(№*×><]+"


def clean_encoding(text):
    return re.sub(r"\(cid:.*\)", "", text)


def remove_uppercase_words(text):
    return re.sub(r"\b[А-ЯЁA-Z]{5,}\b", "", text)


def replace_many_newlines_with_one(text):
    return re.sub(r"\n{2,}", "\n", text)


def replace_spaces_before_punctuation(text):
    return re.sub(r"\s+([.,!?;:])", r"\1", text)


def remove_word_with_ii(text):
    return re.sub(r"\b\w*II\w*\b", "", text)


def add_space_after_comma(text):
    return re.sub(r",(\S)", r", \1", text)


def remove_many_spaces(text):
    return re.sub(r"\s{2,}", " ", text)


def remove_many_dot(text):
    return re.sub(r"\.{3,}", ".", text)


def remove_html_tags(text):
    return re.sub(r"<[^>]+>", "", text)


def remove_emojis(text):
    return re.sub(r"[\U00010000-\U0010ffff]", "", text)


def remove_redundant_punctuation(text):
    return re.sub(r"([,!?])\1+", r"\1", text)


def remove_spaced_letters(text):
    return re.sub(r"\b(?:[А-Яа-яI]\s){2,}[А-Яа-яI]\b", "", text)


def remove_non_whitelisted_chars(text):
    return re.sub(NOT_IN_WHITELIST_REGEX, "", text)


def remove_garbage(text):
    """
    example:
        , : I ? I I, I I! > I I I I. : «, .!» I I, . I, I, , I I, I., I I, , . I

    :param text:
    :return:
    """

    def _clean(line):
        line = re.sub(r"^[ I.,×«»()\-–!№\d?:;]*$", "", line)
        line = re.sub(
            r"^[^АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя]*$",
            "",
            line,
        )
        line = re.sub(r"\, \, ", "", line)
        return line

    return "\n".join(_clean(line) for line in text.split("\n"))


def clean_text(text):
    clean_functions = [
        remove_non_whitelisted_chars,
        remove_html_tags,
        remove_emojis,
        clean_encoding,
        remove_spaced_letters,
        remove_uppercase_words,
        replace_many_newlines_with_one,
        replace_spaces_before_punctuation,
        remove_word_with_ii,
        add_space_after_comma,
        remove_many_spaces,
        remove_many_dot,
        remove_redundant_punctuation,
        remove_garbage,
    ]

    for func in clean_functions:
        text = func(text)

    return text
