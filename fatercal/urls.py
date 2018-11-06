from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^change_ref/(?P<id_taxon>[0-9]+)/$', views.change_taxon_ref, name='change a taxon referent'),
    url(r'^change_sup/(?P<id_taxon>[0-9]+)/$', views.change_taxon_sup, name='change a taxon superior'),
    url(r'^taxon_to_valid/(?P<id_taxon>[0-9]+)/$', views.change_validity_to_valid, name='change taxon to valid'),
    url(r'^advanced_search/$', views.advanced_search, name='Advanced Search'),
    url(r'^export_taxref/$', views.extract_taxon_taxref, name='Export Taxref version'),
    url(r'^export_search_taxref/$', views.extract_search_taxon_taxref, name='Export version Taxref search'),
    url(r'^choose_search_data_taxon/$', views.choose_search_data, name='Choose Taxon data'),
    url(r'^export_search_sample/$', views.extract_search_sample, name='Export sample search'),
    url(r'^export_for_import_sample/$', views.export_for_import_sample, name='Export sample search'),
    url(r'^import_sample/$', views.add_sample_by_csv, name='Import sample'),
    url(r'^export_adv_search/$', views.export_adv_search, name='Export advanced search taxon'),
    url(r'^map_sample/$', views.map_sample, name='Map Sample'),
    url(r'^update_map/$', views.update_map, name='Update Map')
]
