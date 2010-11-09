from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'', include('knowledgebase.urls'))
)

# Serve static files for local dev only
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$','django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT
        }),
    )