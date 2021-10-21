from django.urls import path, re_path, include
from rest_framework import routers
from . import views

urlpatterns = [
    re_path(r'^change_taxon_ref/(?P<id_taxon>[0-9]+)/$', views.change_taxon_ref, name='change_taxon_ref'),
    re_path(r'^change_taxon_sup/(?P<id_taxon>[0-9]+)/$', views.change_taxon_sup, name='change_taxon_sup'),
    re_path(r'^taxon_to_valid/(?P<id_taxon>[0-9]+)/$', views.change_validity_to_valid, name='taxon_to_valid'),
    path('advanced_search/', views.advanced_search, name='advanced_search'),
    path('export_taxref/', views.extract_taxon_taxref, name='export_taxref'),
    path('export_search_taxref/', views.extract_search_taxon_taxref, name='export_search_taxref'),
    path('choose_search_data_taxon/', views.choose_search_data, name='choose_search_data_taxon'),
    path('export_search_sample/', views.extract_search_sample, name='export_search_sample'),
    path('export_for_import_sample/', views.export_for_import_sample, name='export_for_import_sample'),
    path('import_sample/', views.add_sample_by_csv, name='import_sample'),
    path('export_adv_search/', views.export_adv_search, name='export_adv_search'),
    path('map_sample/', views.map_sample, name='map_sample'),
    path('update_map/', views.update_map, name='update_map'),
    path('update_from_taxref/', views.update_from_taxref, name='update_from_taxref'),
    path('insert_from_taxref/', views.insert_from_taxref, name='insert_from_taxref'),
]
