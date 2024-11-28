from taxonomy.lazy import LazyTaxon
from taxonomy.models import TaxonomyModelRouter

# taxonomy only works with TenantTestCase
from django_tenants.test.cases import TenantTestCase

import uuid


TAXON_SOURCE = 'taxonomy.sources.col'

SYNONYM_OF_NATRIX_NATRIX = {
    'name_uuid' : '52a3926b-b950-4315-ab06-06a93a67266b',
    'taxon_latname' : 'Natrix natrix',
    'taxon_author': 'Linnaeus, 1758',
    'taxon_source' : TAXON_SOURCE,
    'preferred_name_uuid' : 'b95b6c5f-47ac-4ad4-bd6a-4158c78165be',
    'taxon_nuid' : '00100800c00301800m002',
}

NATRIX_NATRIX = {
    'name_uuid' : 'b95b6c5f-47ac-4ad4-bd6a-4158c78165be',
    'taxon_latname' : 'Natrix natrix',
    'taxon_author' : '(Linnaeus, 1758)',
    'taxon_nuid' : '00100800c00301800m002',
    'taxon_source' : TAXON_SOURCE,
}


class TestLazyTaxon(TenantTestCase):

    def setUp(self):
        super().setUp()
        self.models = TaxonomyModelRouter(TAXON_SOURCE)



    def compare_taxon_parameters(self, taxon_1, taxon_2):

        for parameter in ['name_uuid', 'taxon_latname', 'taxon_author', 'taxon_nuid', 'taxon_source']:

            if isinstance(taxon_1, dict):
                taxon_1_parameter = taxon_1[parameter]
            else:
                taxon_1_parameter = getattr(taxon_1, parameter)

            if isinstance(taxon_2, dict):
                taxon_2_parameter = taxon_2[parameter]
            else:
                taxon_2_parameter = getattr(taxon_2, parameter)

            if isinstance(taxon_1_parameter, uuid.UUID):
                taxon_1_parameter = str(taxon_1_parameter)

            if isinstance(taxon_2_parameter, uuid.UUID):
                taxon_2_parameter = str(taxon_2_parameter)

            self.assertEqual(taxon_1_parameter, taxon_2_parameter)

    def test__init__(self):
        
        taxon_kwargs = NATRIX_NATRIX
        lazy_taxon = LazyTaxon(**taxon_kwargs)

        self.compare_taxon_parameters(lazy_taxon, NATRIX_NATRIX)
        instance = self.models.TaxonTreeModel.objects.get(name_uuid=taxon_kwargs['name_uuid'])

        lazy_taxon_from_instance = LazyTaxon(instance=instance)
        self.compare_taxon_parameters(lazy_taxon_from_instance, NATRIX_NATRIX)


    def test__init__synonym(self):
        
        taxon_kwargs = SYNONYM_OF_NATRIX_NATRIX
        lazy_taxon = LazyTaxon(**taxon_kwargs)

        self.compare_taxon_parameters(lazy_taxon, SYNONYM_OF_NATRIX_NATRIX)

        # cant be instantiated like this: LazyTaxon(instance=synonym_instance), no taxon_nuid in this instance

    def test_exists_in_tree(self):
        
        taxon_kwargs = NATRIX_NATRIX
        lazy_taxon = LazyTaxon(**taxon_kwargs)

        self.assertTrue(lazy_taxon.exists_in_tree())

        synonym_taxon_kwargs = SYNONYM_OF_NATRIX_NATRIX
        synonym_lazy_taxon = LazyTaxon(**synonym_taxon_kwargs)

        self.assertFalse(synonym_lazy_taxon.exists_in_tree())
        

    def test_tree_instance(self):
        
        taxon_kwargs = NATRIX_NATRIX
        lazy_taxon = LazyTaxon(**taxon_kwargs)

        tree_instance = lazy_taxon.tree_instance()
        expected_tree_instance = self.models.TaxonTreeModel.objects.get(name_uuid=NATRIX_NATRIX['name_uuid'])

        self.assertEqual(tree_instance, expected_tree_instance)

        synonym_taxon_kwargs = SYNONYM_OF_NATRIX_NATRIX
        synonym_lazy_taxon = LazyTaxon(**synonym_taxon_kwargs)

        synonym_tree_instance = synonym_lazy_taxon.tree_instance()

        self.assertEqual(synonym_tree_instance, None)


    def test_synonyms(self):
        
        taxon_kwargs = NATRIX_NATRIX
        lazy_taxon = LazyTaxon(**taxon_kwargs)

        synonyms = lazy_taxon.synonyms()
        synonyms_name_uuids = list(synonyms.values_list('name_uuid', flat=True))
        synonyms_name_uuids = [str(name_uuid) for name_uuid in synonyms_name_uuids]

        self.assertEqual(synonyms.count(), 11)

        synonym_uuid = SYNONYM_OF_NATRIX_NATRIX['name_uuid']

        self.assertTrue(synonym_uuid in synonyms_name_uuids)


    def test_exists_as_synonym(self):
        
        taxon_kwargs = NATRIX_NATRIX
        lazy_taxon = LazyTaxon(**taxon_kwargs)

        self.assertFalse(lazy_taxon.exists_as_synonym())

        synonym_taxon_kwargs = SYNONYM_OF_NATRIX_NATRIX
        synonym_lazy_taxon = LazyTaxon(**synonym_taxon_kwargs)

        self.assertTrue(synonym_lazy_taxon.exists_as_synonym())


    def test_synonym_instance(self):
        
        taxon_kwargs = NATRIX_NATRIX
        lazy_taxon = LazyTaxon(**taxon_kwargs)

        self.assertEqual(lazy_taxon.synonym_instance(), None)

        synonym_taxon_kwargs = SYNONYM_OF_NATRIX_NATRIX
        synonym_lazy_taxon = LazyTaxon(**synonym_taxon_kwargs)

        expected_synonym_instance = self.models.TaxonSynonymModel.objects.get(name_uuid=SYNONYM_OF_NATRIX_NATRIX['name_uuid'])

        self.assertEqual(synonym_lazy_taxon.name_uuid, str(expected_synonym_instance.name_uuid))
        self.assertEqual(synonym_lazy_taxon.taxon_latname, expected_synonym_instance.taxon_latname)
        self.assertEqual(synonym_lazy_taxon.taxon_author, expected_synonym_instance.taxon_author)

    def test_preferred_name_lazy_taxon(self):
        
        taxon_kwargs = NATRIX_NATRIX
        lazy_taxon = LazyTaxon(**taxon_kwargs)

        preferred_name_lazy_taxon = lazy_taxon.preferred_name_lazy_taxon()

        self.compare_taxon_parameters(lazy_taxon, preferred_name_lazy_taxon)

    def test_vernacular(self):
        pass

    def test_all_vernacular_names(self):
        pass

    def test_descendants(self):
        pass