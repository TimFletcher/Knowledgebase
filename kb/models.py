from django.db import models
from tagging.fields import TagField
from django.contrib.auth.models import User
from pygments import formatters, highlight, lexers
import textile

class WithDate(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

# ============================================================================

class Language(WithDate):
    name          = models.CharField(max_length=100)
    slug          = models.SlugField(unique=True)
    language_code = models.CharField(max_length=100)
    mime_type     = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('kb_language_detail', (), {'slug': self.slug})
        
    def get_lexer(self):
        return lexers.get_lexer_by_name(self.language_code)
        
# ============================================================================

class Snippet(WithDate):
    author           = models.ForeignKey(User)
    title            = models.CharField(max_length=200)
    slug             = models.SlugField(unique=True)
    language         = models.ForeignKey(Language)
    description      = models.TextField()
    description_html = models.TextField(editable=False)
    code             = models.TextField()
    highlighted_code = models.TextField(editable=False)
    tags             = TagField()

    class Meta:
        ordering = ['-date_created']

    def __unicode__(self):
        return self.title
    
    def highlight(self):
        return highlight(self.code,
                         self.language.get_lexer(),
                         formatters.HtmlFormatter(linenos=True))

    # For admin only - can't use ModelAdmin method in list_display_links
    def edit(self):
        return 'Edit &raquo;'
    edit.allow_tags = True
    edit.short_description = 'Edit snippet'


    def save(self, force_insert=False, force_update=False):
        self.description_html = textile.textile(self.description.encode('utf-8'),
                                                encoding='utf-8',
                                                output='utf-8')
        self.highlighted_code = self.highlight()
        super(Snippet, self).save(force_insert, force_update)
        
    @models.permalink
    def get_absolute_url(self):
        return ('kb_snippet_detail', (), {'object_id': self.pk})