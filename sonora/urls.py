from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.static import serve

home_view = ensure_csrf_cookie(TemplateView.as_view(template_name="index.html"))

urlpatterns = [
    path("", home_view, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("voice_api.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r"^(?P<path>styles\.css|app\.js)$", serve, {"document_root": settings.BASE_DIR}),
    ]
