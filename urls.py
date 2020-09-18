from django.urls import path
from taxonomy import views

urlpatterns = [
    path('searchtaxon/', views.SearchTaxon.as_view(), name='search_taxon'),
    #path('taxa/<slug:slug>/', views.SpeciesDetail.as_view(), name='species_detail'),
    #path('getWiki/<int:taxon_id>/', views.GetWiki.as_view(), name='get_wiki'),
    # url(r'^request-taxon/$', views.RequestTaxon.as_view(), name='request_taxon'),
    #re_path(r'^get-taxon/(-\w+)/$', views.get_taxon, name='get_taxon'),
    #re_path(r'^get-taxon/([0-9a-z-]+)/(\w+)/$', views.get_taxon, name='get_taxon'),
]

