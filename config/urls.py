from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("config.api_urls")),
    path("api-auth/", include("rest_framework.urls")),

    path("accounts/", include("apps.accounts.urls")),
    path("syllabus/", include("apps.syllabus.urls")),
    path("notes/", include("apps.notes.urls")),
    path("papers/", include("apps.papers.urls")),
    path("timetable/", include("apps.timetable.urls")),
    path("progress/", include("apps.progress.urls")),
    path("tebogo/", include("apps.chatbot.urls")),

    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
