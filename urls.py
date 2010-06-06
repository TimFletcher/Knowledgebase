from django.conf.urls.defaults import *
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)), # Why is this not a string?
    (r'', include('kb.urls'))
)

# Serve static files for local dev only
if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^site_media/(?P<path>.*)$',
                            'django.views.static.serve',
                            {'document_root': '/users/tim/Sites/kb/media'}),
    )