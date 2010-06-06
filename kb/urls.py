from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.date_based import archive_index
from kb.models import Language, Snippet
from tagging.models import Tag
import settings

# Data for generic views
snippets = Snippet.objects.all()
language_info_dict = {
    'queryset': Language.objects.all(),
}
snippet_info_dict = {
    'queryset': snippets,
}
snippet_archive_dict = {
    'queryset': snippets,
    'date_field': 'date_created',
    'template_object_name': 'snippet_list',
}
tag_info_dict = {
    'queryset': Tag.objects.all(),
}

# Views for snippets
urlpatterns = patterns('',
    url(r'^languages/(?P<slug>[-\w]+)/', 'kb.views.languages.language_detail', name='kb_language_detail'),
    url(r'^snippets/(?P<object_id>\d+)/', object_detail, snippet_info_dict, name='kb_snippet_detail'),
    url(r'^tags/(?P<object_id>\d+)/', 'kb.views.tags.tag_detail', name='kb_tag_detail'),
)
    
# Generic list views.
urlpatterns += patterns('',
    url(r'^$', archive_index, snippet_archive_dict, name='kb_index'),
    url(r'^languages/', object_list, language_info_dict, name='kb_language_list'),
    url(r'^snippets/', object_list, dict(snippet_info_dict, template_object_name='snippet'), name='kb_snippet_list'),
    url(r'^tags/', object_list, tag_info_dict, name='kb_tag_list'),
)