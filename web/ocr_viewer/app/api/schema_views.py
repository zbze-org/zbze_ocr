from django.conf import settings
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    # def get_schema(self, *args, **kwargs):
    #     schema = super().get_schema(*args, **kwargs)
    #     schema.basePath = '/api/prefix'  # API prefix
    #     return schema
    pass


BUILD_DATA = {
    'BUILD_BRANCH': settings.BUILD_BRANCH,
    'BUILD_COMMIT_SHA': settings.BUILD_COMMIT_SHA,
    'BUILD_COMMIT_SHORT_SHA': settings.BUILD_COMMIT_SHORT_SHA,
    'BUILD_COMMIT_TIMESTAMP': settings.BUILD_COMMIT_TIMESTAMP,
    'BUILD_JOB_ID': settings.BUILD_JOB_ID,
    'BUILD_PIPELINE_ID': settings.BUILD_PIPELINE_ID,
    'BUILD_VERSION': settings.BUILD_VERSION,
}


def version_view(request):
    return JsonResponse(BUILD_DATA)


def get_schema_version_view(version='v1'):
    build_info = '\n'.join(f'{k}: {v}' for k, v in BUILD_DATA.items())

    description = (
        f'Примеры и неочевидные моменты\n'
        f'snippet: https://gitlab.com/harf-development/harf-api/-/snippets/2216418 \n\n\n'
        f'Build Info\n'
        f'{build_info}'
    )
    schema_view_v1 = get_schema_view(
        openapi.Info(
            title="Harf API",
            default_version=version,
            description=description,
            # terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(name='gitlab', url='https://gitlab.com/harf-development'),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
        # url='http://0.0.0.0',
        # url=settings.API_URL,
        generator_class=CustomOpenAPISchemaGenerator
    )
    return schema_view_v1
