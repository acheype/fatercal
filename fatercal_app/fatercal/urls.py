from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^change_ref/(?P<id_taxon>[0-9]+)/$', views.change_taxon_ref, name='change a taxon referent'),
    re_path(r'^change_sup/(?P<id_taxon>[0-9]+)/$', views.change_taxon_sup, name='change a taxon superior'),
    re_path(r'^taxon_to_valid/(?P<id_taxon>[0-9]+)/$', views.change_validity_to_valid, name='change taxon to valid'),
    path('advanced_search/', views.advanced_search, name='Advanced Search'),
    path('export_taxref/', views.extract_taxon_taxref, name='Export Taxref version'),
    path('export_search_taxref/', views.extract_search_taxon_taxref, name='Export version Taxref search'),
    path('choose_search_data_taxon/', views.choose_search_data, name='Choose Taxon data'),
    path('export_search_sample/', views.extract_search_sample, name='Export sample search'),
    path('export_for_import_sample/', views.export_for_import_sample, name='Export sample search'),
    path('import_sample/', views.add_sample_by_csv, name='Import sample'),
    path('export_adv_search/', views.export_adv_search, name='Export advanced search taxon'),
    path('map_sample/', views.map_sample, name='Map Sample'),
    path('update_map/', views.update_map, name='Update Map'),
    path('update_from_taxref/', views.update_from_taxref, name='Update from Taxref')
]
