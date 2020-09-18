from django.db import models

'''
    enable the Catalogue Of Life
    all LocalCosmos enabled taxonomic dbs need 4 models:
    - *Taxon
    - *TaxonLocale
    - *TaxonNuid
    - *TaxonTree

    plus one TaxonDBManager.py file
'''
from taxonomy.models import TaxonTree, TaxonSynonym, TaxonNamesView, TaxonLocale


class ColTaxonTree(TaxonTree):
    pass


class ColTaxonSynonym(TaxonSynonym):
    taxon = models.ForeignKey(ColTaxonTree, on_delete=models.CASCADE, to_field='name_uuid')

    class Meta:
        unique_together = ('taxon', 'taxon_latname', 'taxon_author')


class ColTaxonLocale(TaxonLocale):
    taxon = models.ForeignKey(ColTaxonTree, on_delete=models.CASCADE, to_field='name_uuid')

    class Meta:
        index_together = [
            ['taxon', 'language'],
        ]
    

'''
    VIEWS
'''
class ColTaxonNamesView(TaxonNamesView):
    pass

