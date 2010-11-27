from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from models import Language, Snippet

snippets = Snippet.objects.published()
snippet_info_dict = {
    'queryset': snippets,
}
language_info_dict = {
    'queryset': Language.objects.all(),
}

urlpatterns = patterns('',
    url(r'^$', object_list, dict(snippet_info_dict, template_object_name='snippet'), name='kb_index'),
    url(r'^snippets/$', object_list, dict(snippet_info_dict, template_object_name='snippet'), name='kb_snippet_list'),
    url(r'^snippets/(?P<object_id>\d+)/$', object_detail, snippet_info_dict, name='kb_snippet_detail'),
    url(r'^languages/$', object_list, language_info_dict, name='kb_language_list'),
    url(r'^languages/(?P<slug>\w+)/$', object_detail, language_info_dict, name='kb_language_detail'),
)