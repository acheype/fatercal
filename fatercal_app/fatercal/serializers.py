from rest_framework import serializers

from .models import Taxon, TaxrefRang, TaxrefHabitat, TaxrefStatus, Vernaculaire


class TaxonSerializer(serializers.HyperlinkedModelSerializer):
    last_update = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S");
    class Meta:
        model = Taxon
        fields = ['url', 'id', 'id_ref', 'id_sup', 'cd_nom', 'cd_ref', 'cd_sup', 'lb_nom', 'lb_auteur', 'nom_complet',
                  'noms_vern', 'rang', 'habitat', 'nc', 'grande_terre', 'iles_loyaute', 'autre', 'remarques', 'sources',
                  'reference_description', 'utilisateur', 'last_update']


class TaxrefRangSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxrefRang
        fields = ['url', 'rang', 'lb_rang']


class TaxrefHabitatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxrefHabitat
        fields = ['url', 'habitat', 'lb_habitat']


class TaxrefStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxrefStatus
        fields = ['url', 'status', 'lb_status']


class VernaculaireSerializer(serializers.HyperlinkedModelSerializer):
    taxon = serializers.HyperlinkedRelatedField(view_name='taxon-detail', read_only='True', source='id_taxon')
    iso639_3 = serializers.CharField(source='iso639_3.iso639_3')

    class Meta:
        model = Vernaculaire
        fields = ['id_taxvern', 'taxon', 'nom_vern', 'pays', 'iso639_3']

