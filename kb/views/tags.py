from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from tagging.models import Tag, TaggedItem
from kb.models import Snippet

def tag_detail(request, object_id):
    tag = get_object_or_404(Tag, pk=object_id)
    return object_list(request,
                       queryset=TaggedItem.objects.get_by_model(Snippet, tag),
                       paginate_by=20,
                       template_name='tagging/tag_detail.html',
                       extra_context={'tag': tag}
    )