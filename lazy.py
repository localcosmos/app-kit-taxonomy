from taxonomy.models import TaxonomyModelRouter, MetaVernacularNames

from django.utils import translation

from localcosmos_server.taxonomy.lazy import LazyTaxonBase


class LazyTaxon(LazyTaxonBase):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # set the correct model classes from self.source
        self.models = TaxonomyModelRouter(self.taxon_source)


    def exists_in_tree(self):
        instance = self.tree_instance()
        if instance:
            return True
        return False

    '''
    the tree instance can be none, if the taxon does not exist anymore in the tree
    - do NOT query by name_uuid, which might change across tree updates
    - DO query taxon_latname AND taxon_author
    '''
    def tree_instance(self):
        query = self.models.TaxonTreeModel.objects.filter(taxon_latname=self.taxon_latname,
                                                             taxon_author=self.taxon_author)

        if query.count() == 1:
            return query.first()

        else:
            instance = self.models.TaxonTreeModel.objects.filter(name_uuid=self.name_uuid).first()

            if instance:
                return instance

        return None


    def exists_as_synonym(self):
        instance = self.synonym_instance()
        if instance:
            return True
        return False
        
    def synonym_instance(self):
        query = self.models.TaxonSynonymModel.objects.filter(taxon_latname=self.taxon_latname,
                                                             taxon_author=self.taxon_author)

        if query.count() == 1:
            return query.first()

        else:
            instance = self.models.TaxonSynonymModel.objects.filter(name_uuid=self.name_uuid).first()

            if instance:
                return instance

        return None
        
    

    def vernacular(self, language=None, cache=None):

        if cache:
            if self.taxon_source in cache and self.taxon_latname in cache[self.taxon_source]:

                cache_entry = cache[self.taxon_source][self.taxon_latname]

                if language in cache_entry:
                    return cache_entry[language]

                return None

        if language == None:
            language = translation.get_language()[:2].lower()

        locale = MetaVernacularNames.objects.filter(taxon_latname=self.taxon_latname,
                    taxon_author=self.taxon_author, language=language, preferred=True).first()


        if not locale:
            locale = self.models.TaxonLocaleModel.objects.filter(taxon__taxon_latname=self.taxon_latname,
                            taxon__taxon_author=self.taxon_author, language=language, preferred=True).first()

        if not locale:
            locale = self.models.TaxonLocaleModel.objects.filter(taxon__taxon_latname=self.taxon_latname,
                            taxon__taxon_author=self.taxon_author, language=language).first()

        if not locale and self.origin == 'MetaNode':
            return self.instance.name
            
        if locale:
            return locale.name            

        return None

    def all_vernacular_names(self, only_preferred=True, cache=None, language=None):

        matches = []

        if not language:
            found_locales = []
            
            locales = MetaVernacularNames.objects.filter(taxon_latname=self.taxon_latname,
                                                         taxon_author=self.taxon_author)

            if only_preferred:
                locales = locales.filter(preferred=True)

            for locale in locales:
                matches.append(locale)
                found_locales.append(locale.language)

            locales = self.models.TaxonLocaleModel.objects.filter(taxon__taxon_latname=self.taxon_latname,
                                        taxon__taxon_author=self.taxon_author).exclude(language__in=found_locales)

            #if only_preferred:
            #    locales = locales.filter(preferred=True)

            for locale in locales:
                matches.append(locale)

        else:
            matches = self.models.TaxonLocaleModel.objects.filter(taxon__taxon_latname=self.taxon_latname,
                                        taxon__taxon_author=self.taxon_author, language=language)

        return matches
        

    def descendants(self):
        return self.models.TaxonTreeModel.objects.filter(taxon_nuid__startswith=self.taxon_nuid)


from localcosmos_server.taxonomy.lazy import LazyTaxonListBase

class LazyTaxonList(LazyTaxonListBase):
    LazyTaxonClass = LazyTaxon
