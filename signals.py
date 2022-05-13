from django.db.models.signals import post_save, post_delete

from taxonomy.sources.custom.models import CustomTaxonTree

from localcosmos_server.taxonomy.generic import ModelWithRequiredTaxon, ModelWithTaxon

def get_subclasses(cls):
    result = []
    classes_to_inspect = [cls]
    
    while classes_to_inspect:
        class_to_inspect = classes_to_inspect.pop()
        
        for subclass in class_to_inspect.__subclasses__():

            if subclass._meta.abstract == True:
                classes_to_inspect.append(subclass)
                
            elif subclass not in result:
                result.append(subclass)
                classes_to_inspect.append(subclass)
                
    return result


"""
    If a user updates an CustomTaxonTree entry all taxon_latnames AND taxon_nuids have to be updated
    - Subclasses of ModelWithTaxon
    - Subclasses of ModelWithRequiredTaxon
"""
def perform_taxon_latname_and_nuid_update(instance, Subclass):
    taxa = Subclass.objects.filter(name_uuid=instance.name_uuid)
    for taxon in taxa:
        taxon.taxon_latname = instance.taxon_latname
        taxon.taxon_author = instance.taxon_author
        taxon.taxon_nuid = instance.taxon_nuid
        taxon.save()
        

def update_taxon_latnames(sender, instance, created, **kwargs):
    
    if created:
        return False

    for Subclass in get_subclasses(ModelWithRequiredTaxon):        
        perform_taxon_latname_and_nuid_update(instance, Subclass)

    for Subclass in get_subclasses(ModelWithTaxon):
        perform_taxon_latname_and_nuid_update(instance, Subclass)


post_save.connect(update_taxon_latnames, CustomTaxonTree)
