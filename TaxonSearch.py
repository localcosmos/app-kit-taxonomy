"""
    a class managing all taxa across different sources
    the search depends on a selected source

    in the end, this should use a NAMES view, not TaxonTree and TaxonLocale models
"""

from django.db.models import Q

from .models import TaxonomyModelRouter

from .lazy import LazyTaxon

class TaxonSearch(object):

    def __init__(self, taxon_source, searchtext, language, *args, **kwargs):

        self.limit = kwargs.get('limit', 10)
        self.min_length = kwargs.get('min_length', 3)

        self.language = language.lower()
        self.taxon_source = taxon_source
        self.searchtext = searchtext.replace('+',' ').upper().strip()

        # get the models from the source
        self.models = TaxonomyModelRouter(taxon_source)
        
        self.latnames_query = []
        self.names_query = []
        self.exact_latnames_query = []
        self.exact_names_query = []
        
        self.queries_ready = False

        self.kwargs = kwargs

    # do not apply limits here, because queries cannot be filtered after slicing
    def make_queries(self):

        self.exact_matches_query = self.models.TaxonNamesModel.objects.filter(
            language__in=['la', self.language], name__iexact=self.searchtext.upper())

        self.matches_query = self.models.TaxonNamesModel.objects.filter(
            language__in=['la', self.language], name__istartswith=self.searchtext.upper())

        self.vernacular_query = self.models.TaxonNamesModel.objects.filter(
            language=self.language, name__icontains=self.searchtext.upper())

        self.queries_ready = True
        

    def get_choices_for_typeahead(self):

        if not self.queries_ready:
            self.make_queries()


        names = list(self.exact_matches_query[:5]) + list(self.matches_query[:self.limit]) + list(self.vernacular_query[:self.limit])
        
        choices = []

        for name in names:

            taxon_kwargs = {
                'taxon_source' : self.taxon_source,
                'taxon_latname' : name.taxon_latname,
                'taxon_author' : name.taxon_author,
                'taxon_nuid' : name.taxon_nuid,
                'name_uuid' : name.name_uuid,
            }
            
            lazy_taxon = LazyTaxon(**taxon_kwargs)

            if name.name_type == 'accepted name':
                label = '{0}'.format(name.name)
            
            elif name.name_type == 'synonym':
                label = '{0} (syn. {1})'.format(name.taxon_latname, name.name)

            elif name.name_type == 'vernacular':
                label = '{0} ({1})'.format(name.name, name.taxon_latname)

            obj = lazy_taxon.as_typeahead_choice(label=label)
            
                
            if obj not in choices:
                choices.append(obj)


        return choices
