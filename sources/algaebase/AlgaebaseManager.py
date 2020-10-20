####################################################################################################################
#
#   IMPORT Algaebase.org
#
####################################################################################################################

from taxonomy.sources.TaxonSourceManager import (TaxonSourceManager, SourceTreeTaxon,
                                    SourceSynonymTaxon, VernacularName, TreeCache)

from taxonomy.sources.algaebase.models import AlgaebaseTaxonTree, AlgaebaseTaxonSynonym, AlgaebaseTaxonLocale

import psycopg2, psycopg2.extras, os, csv

from html.parser import HTMLParser



# the CoL2019 uses language names like "English" -> use langcodes
import langcodes

DEBUG = False



# db interface for algaebase 2020 postgres db
algaebaseCon = psycopg2.connect(dbname="algaebase2019", user="localcosmos", password="localcosmos",
                          host="localhost", port="5432")

algaebaseCursor = algaebaseCon.cursor(cursor_factory = psycopg2.extras.DictCursor)


class AlgaebaseSourceTreeTaxon(SourceTreeTaxon):

    TreeModel = AlgaebaseTaxonTree

    def _get_source_object(self):
        raise NotImplementedError('SourceTaxon subclasses need a _get_source_object method')


    def _get_vernacular_names(self):
        raise NotImplementedError('SourceTaxon subclasses need a _get_vernacular_names method')


    def _get_synonyms(self):
        raise NotImplementedError('SourceTaxon subclasses need a _get_synonyms method')


class AlgaebaseSourceSynonymTaxon(SourceSynonymTaxon):
    pass


class AlgaebaseTreeCache(TreeCache):

    SourceTreeTaxonClass = AlgaebaseSourceTreeTaxon
    TaxonTreeModel = AlgaebaseTaxonTree
    

class AlgaebaseManager(TaxonSourceManager):

    SourceTreeTaxonClass = AlgaebaseSourceTreeTaxon
    SourceSynonymTaxonClass = AlgaebaseSourceSynonymTaxon
    
    TaxonTreeModel = AlgaebaseTaxonTree
    TaxonSynonymModel = AlgaebaseTaxonSynonym
    TaxonLocaleModel = AlgaebaseTaxonLocale

    TreeCacheClass = AlgaebaseTreeCache

    def _get_root_source_taxa(self):
        raise NotImplementedError('Tree Managers need a _get_root_source_taxa method')


    def _get_children(self, source_taxon):
        raise NotImplementedError('Tree Managers need a _get_children method')

    '''
    this function has to travel right and up until the next parent taxon which has not been climbed down
    yet has been found
    returns a source_taxon or None

    EXAMPLE:
    - source_taxon is a taxon without children
    - the next sibling of source taxon might have children -> check all siblings first
    - if no siblings have children, travel up
    '''

    def _get_next_sibling(self, source_taxon):
        raise NotImplementedError('Tree Managers need a _get_next_sibling method')

    # travel one up
    def _get_parent(self, source_taxon):
        raise NotImplementedError('Tree Managers need a _get_parent method')
