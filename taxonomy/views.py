from django.http import HttpResponse
from django.utils.translation import gettext as _

from localcosmos_server.taxonomy.forms import AddSingleTaxonForm

from taxonomy.models import TaxonomyModelRouter

from django.views.generic import TemplateView, FormView

import json


from .TaxonSearch import TaxonSearch

from django.db.models.functions import Length

from app_kit.models import MetaApp


class SearchTaxon(FormView):

    form_class = AddSingleTaxonForm

    def get(self, request, *args, **kwargs):
        limit = request.GET.get('limit', 10)
        searchtext = request.GET.get('searchtext', None)
        language = request.GET.get('language', 'en').lower()
        source = request.GET['taxon_source']

        search = TaxonSearch(source, searchtext, language, **{'limit':limit})

        choices = search.get_choices_for_typeahead()

        return HttpResponse(json.dumps(choices), content_type='application/json')

'''
    Displaying a TreeView
    - DOES NOT WORK ON STANDALONE INSTALLS
    - works with all taxonomic sources
    - start with root taxa
    - make each node expandable
'''
class TaxonTreeView(TemplateView):

    template_name = 'taxonomy/taxontreeview.html'
    tree_entry_template_name = 'taxonomy/treeview_entry.html' # does not exist anymore, needs to be rewritten

    # load_custom_taxon_children is an ajax view (subclass of this one) that does not need app
    load_app_bar = True
    meta_app = None

    def dispatch(self, request, *args, **kwargs):
        self.models = self.get_taxonomy(**kwargs)
        self.taxon = None
        if 'name_uuid' in kwargs:
            self.taxon = self.models.TaxonTreeModel.objects.get(name_uuid=kwargs['name_uuid'])

        # App is not available on standalone installs, but the app taxonomy is
        # importing App outside a class would result in an error on standalone installs
        if self.load_app_bar == True:
            self.meta_app = MetaApp.objects.get(pk=kwargs['meta_app_id'])
            
        return super().dispatch(request, *args, **kwargs)

    def get_root_taxa(self):
        return self.models.TaxonTreeModel.objects.filter(is_root_taxon=True)

    def get_taxa(self):
        if self.taxon:
            children_nuid_length = len(self.taxon.taxon_nuid) + 3
            taxa = self.models.TaxonTreeModel.objects.annotate(nuid_len=Length('taxon_nuid')).filter(
                taxon_nuid__startswith=self.taxon.taxon_nuid, nuid_len=children_nuid_length)
            
        else:
            taxa = self.get_root_taxa()

        return taxa

    def get_taxonomy(self, **kwargs):
        return TaxonomyModelRouter(kwargs['source'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['language'] = kwargs['language']
        context['taxa'] = self.get_taxa()
        context['parent_taxon'] = self.taxon
        context['tree_entry_template'] = self.tree_entry_template_name
        context['meta_app'] = self.meta_app
        return context
        

