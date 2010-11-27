"""
A drop-in chainable manager for providing models with basic search features 
such as +/- modifiers, quoted exact phrases and ordering by relevance. Simply 
assign the SearchableManager to your model and optionally supply the fields to 
search on in either the manager's constructor, as a separate attribute of the 
manager's model, or as an argument to the actual search method. If search 
fields aren't specified then all char-like fields are used.

Usage: 

Class MyModel(models.Model):

    # Some fields to search on.
    title = models.CharField(max_length=100)
    description = models.TextField()

    # Set up the manager and set the searchable fields. Both methods are 
    # demonstrated here, as a constructor and as a separate model attrribute 
    # although only one is required.
    objects = SearchableManager(search_fields=("title", "description"))
    search_fields = ("title", "description")

# This search query excludes 'how', requires 'cow' and uses 'now brown' as an 
# exact phrase. Also shown is the ability to optionally specify the fields to 
# use for this search overriding the fields specified above.
MyModel.objects.search('-how "now brown" +cow', search_fields=("title",))

Credits:
--------

Stephen McDonald <steve@jupo.org>

License:
--------

Creative Commons Attribution-Share Alike 3.0 License
http://creativecommons.org/licenses/by-sa/3.0/

When attributing this work, you must maintain the Credits
paragraph above.
"""

from operator import ior, iand
from string import punctuation

from django.db.models import Manager, Q, CharField, TextField
from django.db.models.query import QuerySet


class SearchableQuerySet(QuerySet):
    
    def __init__(self, *args, **kwargs):
        self._search_ordered = False
        self._search_terms = set()
        self._search_fields = set(kwargs.pop("search_fields", []))
        super(SearchableQuerySet, self).__init__(*args, **kwargs)

    def search(self, query, search_fields=None):
        """
        Build a queryset matching words in the given search query, treating 
        quoted terms as exact phrases and taking into account + and - symbols as 
        modifiers controlling which terms to require and exclude.
        """
        
        # Use fields arg if given, otherwise check internal list which if empty, 
        # populate from model attr or char-like fields.
        if search_fields is None:
            search_fields = self._search_fields
        if len(search_fields) == 0:
        	search_fields = getattr(self.model, "search_fields", [])
        if len(search_fields) == 0:
            search_fields = [f.name for f in self.model._meta.fields
                if issubclass(f.__class__, CharField) or 
                issubclass(f.__class__, TextField)]
        if len(search_fields) == 0:
        	return self.none()
        self._search_fields.update(search_fields)

        # Remove extra spaces, put modifiers inside quoted terms.
        terms = " ".join(query.split()).replace("+ ", "+").replace('+"', '"+'
            ).replace("- ", "-").replace('-"', '"-').split('"')
        # Strip punctuation other than modifiers from terms and create term 
        # list first from quoted terms, and then remaining words.
        terms = [("" if t[0] not in "+-" else t[0]) + t.strip(punctuation) 
            for t in terms[1::2] + "".join(terms[::2]).split()]
        # Append terms to internal list for sorting when results are iterated.
        self._search_terms.update([t.lower().strip(punctuation) 
            for t in terms if t[0] != "-"])

        # Create the queryset combining each set of terms.
        excluded = [reduce(iand, [~Q(**{"%s__icontains" % f: t[1:]})
            for f in search_fields]) for t in terms if t[0] == "-"]
        required = [reduce(ior, [Q(**{"%s__icontains" % f: t[1:]})
            for f in search_fields]) for t in terms if t[0] == "+"]
        optional = [reduce(ior, [Q(**{"%s__icontains" % f: t})
            for f in search_fields]) for t in terms if t[0] not in "+-"]
        queryset = self
        if excluded:
            queryset = queryset.filter(reduce(iand, excluded))
        if required:
            queryset = queryset.filter(reduce(iand, required))
        # Optional terms aren't relevant to the filter if there are terms
        # that are explicitly required
        elif optional:
            queryset = queryset.filter(reduce(ior, optional))
        return queryset

    def _clone(self, *args, **kwargs):
        """
        Ensure attributes are copied to subsequent queries.
        """
        for attr in ("_search_terms", "_search_fields", "_search_ordered"):
            kwargs[attr] = getattr(self, attr)
        return super(SearchableQuerySet, self)._clone(*args, **kwargs)
    
    def order_by(self, *field_names):
        """
        Mark the filter as being ordered if search has occurred.
        """
        if not self._search_ordered:
            self._search_ordered = len(self._search_terms) > 0
        return super(SearchableQuerySet, self).order_by(*field_names)
        
    def iterator(self):
        """
        If search has occured and no ordering has occurred, sort the results by 
        number of occurrences of terms.
        """
        results = super(SearchableQuerySet, self).iterator()
        if self._search_terms and not self._search_ordered:
            sort_key = lambda obj: sum([getattr(obj, f).lower().count(t.lower()) 
                for f in self._search_fields for t in self._search_terms 
                if getattr(obj, f)])
            return iter(sorted(results, key=sort_key, reverse=True))
        return results

class SearchableManager(Manager):
    """
    Manager providing a chainable queryset.
    Adapted from http://www.djangosnippets.org/snippets/562/
    """
    
    def __init__(self, *args, **kwargs):
        self._search_fields = kwargs.pop("search_fields", [])
        super(SearchableManager, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return SearchableQuerySet(self.model, search_fields=self._search_fields)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)


class SnippetManager(Manager):
    def published(self):
        return self.get_query_set().filter(status=self.model.PUBLISHED)