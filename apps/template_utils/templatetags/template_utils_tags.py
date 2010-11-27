from django import template

register = template.Library()

@register.simple_tag
def active(request, pattern):
    # Scan through a string, looking for any location where this regex matches
    import re
    if re.search(pattern, request.path):
        return 'current'
    return ''