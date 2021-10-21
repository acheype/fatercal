from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.fatercal_api, name='api'),
    path('taxons/search/', views.TaxonSearchViewSet.as_view(), name='taxon-search'),
    path('taxons/', views.TaxonViewSet.as_view({'get': 'list'}), name='taxon-list'),
    path('taxons/<int:pk>/', views.TaxonViewSet.as_view({'get': 'retrieve'}), name='taxon-detail'),
    path('rangs/', views.TaxrefRangViewSet.as_view({'get': 'list'}), name='taxrefrang-list'),
    re_path(r'^rangs/(?P<pk>[a-zA-Z]{2,4})/$', views.TaxrefRangViewSet.as_view({'get': 'retrieve'}),
            name='taxrefrang-detail'),
    path('habitats/', views.TaxrefHabitatViewSet.as_view({'get': 'list'}), name='taxrefhabitat-list'),
    path('habitats/<int:pk>/', views.TaxrefHabitatViewSet.as_view({'get': 'retrieve'}),
         name='taxrefhabitat-detail'),
    path('status/', views.TaxrefStatusViewSet.as_view({'get': 'list'}), name='taxrefstatus-list'),
    re_path(r'^status/(?P<pk>[A-Z]{1})/$', views.TaxrefStatusViewSet.as_view({'get': 'retrieve'}),
            name='taxrefstatus-detail'),
    path('vernaculaires/', views.VernaculaireViewSet.as_view({'get': 'list'}), name='vernaculaire-list'),
    path('vernaculaires/<int:pk>/', views.VernaculaireViewSet.as_view({'get': 'retrieve'}),
         name='vernaculaire-detail'),
]
