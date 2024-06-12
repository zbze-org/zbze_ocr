from rest_framework import serializers

from ocr.models import OcrPageText, OcrBoxText


class SpellErrorSerializer(serializers.Serializer):
    slug = serializers.CharField(max_length=255)
    verbose = serializers.CharField(max_length=255)


class WordTokenSerializer(serializers.Serializer):
    morphemes = serializers.CharField(max_length=255)
    tokens = serializers.ListField(child=serializers.CharField(max_length=255))
    token_ids = serializers.ListField(child=serializers.IntegerField())
    tokens_count = serializers.IntegerField()
    tokenizer = serializers.CharField(max_length=255)


class SuggestionsSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=255)
    frequency = serializers.IntegerField()


class CorrectionCandidateSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=255)
    frequency = serializers.IntegerField()
    distance = serializers.IntegerField()


class ErrorSpanSerializer(serializers.Serializer):
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    error = serializers.CharField(max_length=255)


class OcrWordSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=255)
    frequency = serializers.IntegerField()

    word_tokens = WordTokenSerializer(many=True)
    spell_errors = SpellErrorSerializer(many=True)
    error_spans = ErrorSpanSerializer(many=True)

    is_word_exist_dawg = serializers.BooleanField()

    correction_candidates = CorrectionCandidateSerializer(many=True)
    best_candidate = serializers.CharField(max_length=255)

    image_link = serializers.CharField(max_length=255)
    image_coords = serializers.ListField(child=serializers.IntegerField(), min_length=4, max_length=4)
    confidence = serializers.FloatField()


class SpellCheckSerializer(serializers.Serializer):
    text = serializers.CharField()


class DiffCheckSerializer(serializers.Serializer):
    text1 = serializers.CharField()
    text2 = serializers.CharField()


class DiffCheckResultSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=255)
    line_number = serializers.IntegerField()
    content = serializers.CharField()


class SpellCheckMarkerSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=255)
    severity = serializers.IntegerField()
    startLineNumber = serializers.IntegerField()
    endLineNumber = serializers.IntegerField()
    startColumn = serializers.IntegerField()
    endColumn = serializers.IntegerField()


class SpellCheckResponseSerializer(serializers.Serializer):
    markers = SpellCheckMarkerSerializer(many=True)


class OcrBoxTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcrBoxText
        fields = '__all__'


class OcrBoxTextUpdateSerializer(serializers.Serializer):
    box_image_id = serializers.IntegerField(required=True)
    text = serializers.CharField(max_length=255)


class OcrPageTextSerializer(serializers.ModelSerializer):
    history_id = serializers.IntegerField(required=False)

    class Meta:
        model = OcrPageText
        fields = '__all__'


class OcrPageTextUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcrPageText
        fields = ['text']


class OcrPageTextHistoryLiteSerializer(serializers.ModelSerializer):
    history_id = serializers.IntegerField(required=True)

    class Meta:
        model = OcrPageText
        fields = [
            'id',
            'history_id',
            'md5_hash',
            'is_cleaned',
            'created_at',
            'updated_at',
        ]
