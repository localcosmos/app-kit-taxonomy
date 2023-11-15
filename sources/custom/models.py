from django.db import models

"""
    Taxon classes for taxa created and defined by the user
"""
from taxonomy.models import TaxonTree, TaxonSynonym, TaxonNamesView, TaxonLocale

class CustomTaxonTree(TaxonTree):
    class Meta:
        verbose_name = 'Custom Taxonomy'


class CustomTaxonSynonym(TaxonSynonym):
    taxon = models.ForeignKey(CustomTaxonTree, on_delete=models.CASCADE, to_field='name_uuid')

    class Meta:
        unique_together = ('taxon', 'taxon_latname', 'taxon_author')


class CustomTaxonLocale(TaxonLocale):
    taxon = models.ForeignKey(CustomTaxonTree, on_delete=models.CASCADE, to_field='name_uuid')

    class Meta:
        unique_together = ('taxon', 'language', 'name')


class CustomTaxonNamesView(TaxonNamesView):
    pass
