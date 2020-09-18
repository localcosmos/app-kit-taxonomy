'''
    CUSTOM TAXA
    - requires taxonomy.sources.custom
    - these view have to live within app_kit context as they require an App
    - the standalone uses taxonomy as a service - TaaS for querying custom taxa etc
    - alternatively fills its own db by querying a service - on demand
'''
from django.views.generic import TemplateView, FormView

from .forms import ManageCustomTaxonForm, MoveCustomTaxonForm

from taxonomy.models import TaxonomyModelRouter
from taxonomy.sources.TaxonSourceManager import d2n
from taxonomy.utils import NuidManager
from taxonomy.lazy import LazyTaxon

from django.utils.decorators import method_decorator
from localcosmos_server.decorators import ajax_required


custom_taxon_models = TaxonomyModelRouter('taxonomy.sources.custom')

from django.db.models import CharField
from django.db.models.functions import Length
CharField.register_lookup(Length, 'length')

class ManageCustomTaxon(FormView):

    template_name = 'custom_taxonomy/manage_custom_taxon.html'

    form_class = ManageCustomTaxonForm

    @method_decorator(ajax_required)
    def dispatch(self, request, *args, **kwargs):
        self.taxon = None
        self.parent_taxon = None
        self.locale = None
        self.language = kwargs['language']
        
        if 'name_uuid' in kwargs:
            self.taxon = custom_taxon_models.TaxonTreeModel.objects.get(name_uuid=kwargs['name_uuid'])

            self.locale = custom_taxon_models.TaxonLocaleModel.objects.filter(
                taxon_id=str(self.taxon.name_uuid), language=self.language).first()

            if not self.taxon.is_root_taxon:
                self.parent_taxon = custom_taxon_models.TaxonTreeModel.objects.get(
                    taxon_nuid=str(self.taxon.taxon_nuid)[:-3])

        if self.parent_taxon == None and 'parent_name_uuid' in kwargs:
            self.parent_taxon = custom_taxon_models.TaxonTreeModel.objects.get(
                name_uuid=kwargs['parent_name_uuid'])
        
        return super().dispatch(request, *args, **kwargs)


    def get_initial(self):

        if self.taxon is not None:
            
            initial = {
                'name_uuid' : self.taxon.name_uuid,
                'latname' : self.taxon.taxon_latname,
                'rank' : self.taxon.rank,
                'author' : self.taxon.author,
            }

            if self.locale:
                initial['name'] = self.locale.name
                    
        else:
            initial = {}

        if self.parent_taxon is not None:
            initial['parent_name_uuid'] = self.parent_taxon.name_uuid
        return initial


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['language'] = self.language
        context['taxon'] = self.taxon
        context['parent_taxon'] = self.parent_taxon
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['language'] = self.language
        return form_kwargs

    def form_valid(self, form):
        context = self.get_context_data(**self.kwargs)
        
        created = False
        
        if self.taxon is None:
            created = True

            nuidmanager = NuidManager()

            if self.parent_taxon:
                parent_nuid = self.parent_taxon.taxon_nuid
                children_nuid_length = len(parent_nuid) + 3

                last_sibling = custom_taxon_models.TaxonTreeModel.objects.filter(taxon_nuid__startswith=parent_nuid,
                    taxon_nuid__length=children_nuid_length).order_by('taxon_nuid').last()
                
            else:
                parent_nuid = ''
                # it is a new root_taxon
                last_sibling = custom_taxon_models.TaxonTreeModel.objects.filter(
                    is_root_taxon=True).order_by('id').last()

            # create the nuid
            if last_sibling:
                nuid = nuidmanager.next_nuid(last_sibling.taxon_nuid)
            else:
                nuid = '%s%s' % (parent_nuid, nuidmanager.decimal_to_nuid(1))

            # create the taxon .create(nuid, latname, source_id, **extra_fields)

            extra_fields = {
                'rank' : form.cleaned_data.get('rank', None),
                'author' : form.cleaned_data.get('author', None),
            }

            if not self.parent_taxon:
                extra_fields['is_root_taxon'] = True
            
            self.taxon = custom_taxon_models.TaxonTreeModel.objects.create(
                        nuid,
                        form.cleaned_data['latname'],
                        nuid,
                        **extra_fields
                    )

        else:
            self.taxon.taxon_latname = form.cleaned_data['latname']
            self.taxon.rank = form.cleaned_data.get('rank', None)
            self.taxon.author = form.cleaned_data.get('author', None)

            self.taxon.save()


        if self.locale is None:
            self.locale = custom_taxon_models.TaxonLocaleModel.objects.create(
                self.taxon, form.cleaned_data['name'], form.cleaned_data['input_language'],
                preferred = True,
            )

        else:
            self.locale.name = form.cleaned_data['name']
            self.locale.save()

        context['form'] = form
        context['success'] = True
        context['created'] = created
        context['taxon'] = LazyTaxon(instance=self.taxon)
        return self.render_to_response(context)


from localcosmos_server.generic_views import AjaxDeleteView
class DeleteTaxon(AjaxDeleteView):
    model = custom_taxon_models.TaxonTreeModel

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        context['deleted_object_id'] = self.object.pk
        context['deleted'] = True

        self.model.objects.filter(taxon_nuid__startswith=self.object.taxon_nuid).delete()
        return self.render_to_response(context)


from taxonomy.views import TaxonTreeView
'''
    - create the three root taxa (Animalia, Plantae, Fungi) if not yet present
'''
class ManageCustomTaxonTree(TaxonTreeView):

    template_name = 'custom_taxonomy/manage_custom_taxonomy.html'
    tree_entry_template_name = 'custom_taxonomy/manage_tree_entry.html'

    initial_root_taxa = ['Animalia','Fungi','Plantae']

    def create_initial_root_taxa(self):

        nuidmanager = NuidManager()

        for counter, latname in enumerate(self.initial_root_taxa, 1):
            source_id = counter
            nuid = nuidmanager.decimal_to_nuid(counter)
            self.models.TaxonTreeModel.objects.create(nuid, latname, source_id, is_root_taxon=True, rank='kingdom')


    def get_root_taxa(self):
        root_taxa = self.models.TaxonTreeModel.objects.filter(is_root_taxon=True)

        if not root_taxa:
            self.create_initial_root_taxa()
            root_taxa = self.models.TaxonTreeModel.objects.filter(is_root_taxon=True)

        for taxon in root_taxa:
            if taxon.taxon_latname in self.initial_root_taxa:
                taxon.is_locked = True

        return root_taxa

    def get_taxonomy(self, **kwargs):
        return TaxonomyModelRouter('taxonomy.sources.custom')


class ManageCustomTaxonChildren(ManageCustomTaxonTree):
    template_name = 'taxonomy/treeview_children.html'
    load_app_bar = False

    

'''
    moving has to update across lazy taxa
    moving is currently disabled because of nuid problems when moving a taxon
    moving a taxon would require updating all nuids of all descendant taxa across all ModelWithTaxon subclasses
'''
from taxonomy.signals import get_subclasses
from localcosmos_server.taxonomy.generic import ModelWithRequiredTaxon, ModelWithTaxon


class MoveCustomTaxonTreeEntry(FormView):

    template_name = 'custom_taxonomy/move_custom_taxon.html'
    form_class = MoveCustomTaxonForm

    @method_decorator(ajax_required)
    def dispatch(self, request, *args, **kwargs):
        self.taxon = custom_taxon_models.TaxonTreeModel.objects.get(name_uuid=kwargs['name_uuid'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxon'] = self.taxon
        return context

    def get_initial(self):

        initial = {
            'name_uuid' : self.taxon.name_uuid,
        }

        return initial


    def _update_nuids(self, taxon, Subclass):
        taxa = Subclass.objects.filter(name_uuid=taxon.name_uuid)
        for model_with_taxon in taxa:
            model_with_taxon.taxon_nuid = taxon.taxon_nuid
            model_with_taxon.save()

    def _update_lazy_taxa(self, taxon):
        for Subclass in get_subclasses(ModelWithRequiredTaxon):
            self._update_nuids(taxon, Subclass)

        for Subclass in get_subclasses(ModelWithTaxon):
            self._update_nuids(taxon, Subclass)

    def form_valid(self, form):
        context = self.get_context_data(**self.kwargs)

        # move the taxon, use the form taxon as this has been validated against the new parent taxon
        # a signal adjusts all nuids of the lazy taxa
        form_taxon = custom_taxon_models.TaxonTreeModel.objects.get(name_uuid=form.cleaned_data['name_uuid'])
        new_parent_taxon = form.cleaned_data['new_parent_taxon']

        new_nuid_prefix = new_parent_taxon.taxon_nuid
        old_nuid_prefix = form_taxon.taxon_nuid[:-3]

        for taxon in custom_taxon_models.TaxonTreeModel.objects.filter(taxon_nuid__startswith=form_taxon.taxon_nuid):

            taxon.taxon_nuid = taxon.taxon_nuid.replace(old_nuid_prefix, new_nuid_prefix, 1)
            taxon.save()

            self._update_lazy_taxa(taxon)

        context['new_parent_taxon'] = new_parent_taxon
        context['success'] = True
        context['form'] = form
        return self.render_to_response(context)
