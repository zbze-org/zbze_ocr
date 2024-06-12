from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet

from ocr.models import OcrPageText, OcrBoxText
from ocr.serializers import (
    OcrWordSerializer, SuggestionsSerializer,
    SpellCheckSerializer, SpellCheckResponseSerializer, OcrPageTextSerializer, OcrPageTextHistoryLiteSerializer,
    DiffCheckSerializer, DiffCheckResultSerializer, OcrPageTextUpdateSerializer, OcrBoxTextSerializer,
    OcrBoxTextUpdateSerializer
)
from ocr.services.diff_service import generate_text_diff
from ocr.services.spell_check_service import SpellCheckService
from ocr.services.word_service import ocr_word_service

word_parameter = openapi.Parameter(
    'word',
    openapi.IN_QUERY,
    required=True,
    description="word param",
    type=openapi.TYPE_STRING
)


class OcrBoxTextViewSet(GenericViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = OcrBoxTextSerializer
    queryset = OcrBoxText.objects.all()

    @swagger_auto_schema(
        request_body=OcrBoxTextUpdateSerializer,
        responses={
            201: OcrPageTextSerializer
        }
    )
    @action(detail=False, methods=['post'])
    def update_text(self, request, *args, **kwargs):
        serializer = OcrBoxTextUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            obj = OcrBoxText.objects.get(
                ocr_box_image_id=serializer.validated_data['box_image_id']
            )
        except OcrBoxText.DoesNotExist:
            resp_data = {
                'error': 'Object not found'
            }
            return Response(resp_data, status=404)

        obj.text = serializer.validated_data['text']
        obj.save()

        resp_data = OcrBoxTextSerializer(obj).data

        return Response(resp_data, status=201)


class OcrPageTextViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    authentication_classes = []
    permission_classes = []
    serializer_class = OcrPageTextSerializer
    queryset = OcrPageText.objects.all()

    @swagger_auto_schema(
        request_body=OcrPageTextUpdateSerializer,
        responses={
            201: OcrPageTextSerializer
        }
    )
    @action(detail=True, methods=['post'])
    def update_text(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        serializer = OcrPageTextUpdateSerializer(data=request.data, instance=obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        current_version = obj.history.latest('history_id')
        prev_version = current_version.prev_record
        diff_data = generate_text_diff(text1=prev_version.text, text2=current_version.text)

        return Response(diff_data)

    @action(detail=True, methods=['get'])
    def history_list(self, request, *args, **kwargs):
        text_obj = self.get_object()
        queryset = text_obj.history.all()
        serializer = OcrPageTextHistoryLiteSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='history_detail/(?P<history_id>[^/.]+)')
    def history_detail(self, request, pk=None, history_id=None, *args, **kwargs):
        text_obj = self.get_object()
        queryset = text_obj.history.get(history_id=history_id)
        serializer = OcrPageTextSerializer(queryset)
        return Response(serializer.data)


class OcrViewSet(GenericViewSet):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        request_body=OcrWordSerializer,
        responses={
            201: OcrWordSerializer
        }
    )
    @action(detail=False, methods=['post'])
    def get_word_info(self, request):
        word = request.data['word']
        ocr_page_id = request.data.get('ocr_page_id')

        ocr_word_data = ocr_word_service.get_ocr_word_data(word=word, ocr_page_id=ocr_page_id)
        serializer = OcrWordSerializer(instance=ocr_word_data)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[word_parameter])
    @action(detail=False, methods=['get'])
    def get_suggestions(self, request):
        correction_candidates = ocr_word_service.get_suggestions(word=request.GET.get('word'), limit=50)
        serializer = SuggestionsSerializer(instance=correction_candidates, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SpellCheckSerializer,
        responses={
            200: SpellCheckResponseSerializer
        }
    )
    @action(detail=False, methods=['post'])
    def spell_check(self, request):
        text = request.data['text']
        markers = SpellCheckService().check(text=text)
        serializer = SpellCheckResponseSerializer(instance={'markers': markers})
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=DiffCheckSerializer,
        responses={
            200: DiffCheckResultSerializer
        }
    )
    @action(detail=False, methods=['post'])
    def diff_check(self, request):
        serializer = DiffCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = generate_text_diff(text1=serializer.data['text1'], text2=serializer.data['text2'])
        serializer = DiffCheckResultSerializer(instance=result, many=True)
        return Response(serializer.data)
