class Stemmer:
    def __init__(self, rules):
        self.rules = rules

    def stem(self, word):
        for rule in self.rules:
            new_word, applied = rule.apply(word)
            if applied:
                return new_word
        return word

    def find_possible_stems(self, word):
        possible_stems = []
        for rule in self.rules:
            possible_stems.extend(rule.find_possible_stems(word))
        return possible_stems

    def find_suitable_templates(self, word):
        suitable_templates = []
        for rule in self.rules:
            suitable_templates.extend(rule.find_suitable_templates(word))
        return suitable_templates
