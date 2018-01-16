from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^change_ref/(?P<id_taxon>[0-9]+)/$', views.change_taxon_ref, name='change_taxon_ref'),
    url(r'^change_sup/(?P<id_taxon>[0-9]+)/$', views.change_taxon_sup, name='change_taxon_sup'),
]