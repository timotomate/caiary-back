from django.urls import include, path, re_path
from django.contrib import admin
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()

schema_urlpatterns = [
    path('users/', include('users.urls')),
    path('articles/', include('articles.urls')),
]

schema_view_v1 = get_schema_view(
    openapi.Info(
        title='카이어리 API',
        default_version='v1',
        description='모든 API(로그인 제외)는 로그인을 통해 가져온 액세스 토큰을 Authorization 헤더에 포함해야 합니다. Swagger에서는     하단의 Authorize 버튼으로 입력할 수 있습니다.',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=schema_urlpatterns
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('users/', include('users.urls')),
    path('articles/', include('articles.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view_v1.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view_v1.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view_v1.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
