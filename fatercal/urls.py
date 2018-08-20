from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^change_ref/(?P<id_taxon>[0-9]+)/$', views.change_taxon_ref, name='change a taxon referent'),
    url(r'^change_sup/(?P<id_taxon>[0-9]+)/$', views.change_taxon_sup, name='change a taxon superior'),
    url(r'^export_taxref/$', views.extract_taxon_taxref, name='Export version Taxref'),
    url(r'^taxon_to_valid/(?P<id_taxon>[0-9]+)/$', views.change_validity_to_valid, name='change taxon to valid'),
]