from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from kb.models import Language

def language_detail(request, slug):
    language = get_object_or_404(Language, slug=slug)
    return object_list(request,
                       queryset=language.snippet_set.all(),
                       paginate_by=20,
                       template_name='kb/language_detail.html',
                       extra_context={'language': language}
    )
    
    # If the template name was left out it would default to
    # kb/snippet_list.html. It uses the model of the passed queryset to
    # determine the first half of the filename.