from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^cameraUpload/', include('cameraUpload.urls', namespace="cameraUpload")),
    url(r'^admin/', include(admin.site.urls)),
)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
