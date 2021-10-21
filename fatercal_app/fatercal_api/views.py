from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from fatercal.models import Taxon, TaxrefRang, TaxrefHabitat, TaxrefStatus, Vernaculaire
from .serializers import TaxonSerializer, TaxrefRangSerializer, TaxrefHabitatSerializer, TaxrefStatusSerializer, \
    VernaculaireSerializer
from rest_framework import viewsets, generics


@api_view(['GET'])
def fatercal_api(request, format=None):
    """
        Le référentiel **FATERCAL** concerne l'**ensemble de la faune continentale** (terrestre, eau douce, milieu saumâtre et
        frange littorale soumise à l'influence marine comme par exemple les tortues marines ou les serpents marins) **de
        la Nouvelle-Calédonie** et inclut également les espèces animales dont l'extinction a eu lieu depuis l'arrivée de
        l'Homme il y a plus de 3000 ans. Le périmètre concerne aussi bien la faune native que la faune introduite y
        compris domestique. Ce référentiel fournit donc la liste des noms scientifiques valides et de leurs synonymes
        reflétant les connaissances taxonomiques à un temps donné.

        Seuls les noms disponibles au sens des codes de nomenclature zoologique (ICZN) sont donnés. Par ailleurs, pour
        chaque taxon, il fournit le statut d'endémicité ou non du taxon considéré (espèce et rang infra-spécifique,
        genre, sous genre, tribu, sous famille et famille). Pour chaque taxon, l'information de la présence sur la
        grande terre et les îles loyauté est renseignée.

        FATERCAL permet également de gérer les données de distribution des espèces avec le reférencement de prélèvements
        ainsi que les hôtes et parasites des taxon considérés. Toutefois, l'API rend public uniquement les données
        taxonomique.

        Avec les urls listées ci-dessous, vous pouvez obtenir la liste de chaque type d'objet nécessaire à la
        représentation des données taxonomique de FATERCAL : les **taxons**, les **rangs**, les **habitats**,
        **status** et les **noms vernaculaires**. De plus, chaque objet peut être accédé directement en rajoutant son
        *id* à la fin de l'url. Par exemple, [http://fatercal.ird.nc/api/taxons/1](http://fatercal.ird.nc/api/taxons/1)
        permet d'accéder au taxon avec l'*id 1*, soit le taxon *Biota* de rang *Domaine*.

        Pour permettre la recherche au sein des nombreux taxons, il est possible d'utiliser l'url
        [http://fatercal.ird.nc/api/taxons/search/](http://fatercal.ird.nc/api/taxons/search) et de spécifier en
        paramètre de l'url les champs sur lesquels vous voulez filtrer (plus de détails est donnée à cette adresse).
    """
    return Response({
        'taxons': reverse('taxon-list', request=request, format=format),
        'rangs': reverse('taxrefrang-list', request=request, format=format),
        'habitats': reverse('taxrefhabitat-list', request=request, format=format),
        'status': reverse('taxrefstatus-list', request=request, format=format),
        'vernaculaires': reverse('vernaculaire-list', request=request, format=format),
    })


class TaxonViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Un taxon correspond à une unité taxonomique, c'est à dire tout rang taxonomique au sein de l'arborescence de
        la classification hérarchique du vivant.

        Détails des champs :

          - `url` : lien d'accès à la description du taxon
          - `id` : identifiant FATERCAL du taxon
          - `id_ref` : identifiant FATERCAL du taxon référent (notamment si synonyme)
          - `id_sup` : identifiant FATERCAL du taxon parent, c'est à dire du taxon du rang supérieur au taxon concerné
          (par exemple *Genre* pour le rang *Espèce*)
          - `cd_nom` : identifiant TAXREF du taxon
          - `cd_ref` : identifiant TAXREF du taxon référent
          - `cd_sup` : identifiant TAXFEF du taxon parent
          - `lb_nom` : nom scientifique du taxon
          - `lb_auteur` : autorité du taxon, c'est à dire auteur et date de description
          - `nom_complet` : combinaison du nom scientifique et de l'autorité taxonomique associée
          - `nom_vern` : liste des noms vernaculaires donnés au taxon
          - `rang` : rang taxonomique du taxon au sein de la classification hiérarchique taxonomique du règne animal,
          dont la liste des valeurs est identique à celles de TAXREF
          - `habitat`: code de la catégorie d'habitats utilisées par le taxon (*Terrestre*, *Eau douce*, etc.) dont la
          liste des valeurs est identique à celles de TAXREF
          - `nc` : statut biogéographique par rapport à la NC (*Endémique*, *Natif*, *Introduit*, etc.) dont la liste
          des valeurs est identique à celles de TAXREF
          - `grande_terre` : présence sur la grande terre (y compris Île des pins et Belep)
          - `iles_loyaute` : présence sur au moins une des iles loyauté
          - `autre` : présence hors Nouvelle-Calédonie
          - `sources` : sources bibliographiques pour occurence en Nouvelle-Calédonie, seules l'année et l'auteur sont
          renseignés, plusieurs sources sont séparées par des ;
          - `reference_description` : reférence bibliographique de la description originale du taxon, description
          textuelle de la référence pas toujours précise
          - `utilisateur` : identifiant de l'utilisateur ayant effectué la dernière mise à jour
          - `last_update` : date et heure de la dernière mise à jour

    """
    queryset = Taxon.objects.all()
    serializer_class = TaxonSerializer


class TaxrefRangViewSet(viewsets.ReadOnlyModelViewSet):
    """
        RANG This viewset automatically provides `list` and `retrieve` actions for the REST API
    """
    queryset = TaxrefRang.objects.all()
    serializer_class = TaxrefRangSerializer


class TaxrefHabitatViewSet(viewsets.ReadOnlyModelViewSet):
    """
        HABITAT This viewset automatically provides `list` and `retrieve` actions for the REST API
    """
    queryset = TaxrefHabitat.objects.all()
    serializer_class = TaxrefHabitatSerializer


class TaxrefStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
        STATUS This viewset automatically provides `list` and `retrieve` actions for the REST API
    """
    queryset = TaxrefStatus.objects.all()
    serializer_class = TaxrefStatusSerializer


class VernaculaireViewSet(viewsets.ReadOnlyModelViewSet):
    """
        VERNACULAIRE This viewset automatically provides `list` and `retrieve` actions for the REST API
    """
    queryset = Vernaculaire.objects.all()
    serializer_class = VernaculaireSerializer


class TaxonSearchViewSet(generics.ListAPIView):
    """
        Search a taxon
    """
    serializer_class = TaxonSerializer
    GET_PARAMS_FOR_EQUALS_FILTER = ['id', 'id_ref', 'id_sup', 'cd_nom', 'cd_ref', 'cd_sup', 'grande_terre',
                                    'iles_loyaute', 'autre', 'utilisateur', 'rang', 'habitat',
                                    'nc']
    # TODO search also in noms_vern
    GET_PARAMS_FOR_ICONTAINS_FILTER = ['lb_nom', 'lb_auteur', 'nom_complet', 'sources',
                                       'reference_description', 'last_update']

    def __set_filter_params(self, params):
        for key in self.GET_PARAMS_FOR_EQUALS_FILTER:
            if self.request.query_params.get(key):
                # to make the request simpler for users, replace the chained attributes by the name of the first
                # attribute
                if key == 'rang':
                    params_key = key.replace('rang', 'rang__rang')
                elif key == 'habitat':
                    params_key = key.replace('habitat', 'habitat__habitat')
                elif key == 'nc':
                    params_key = key.replace('nc', 'nc__status')
                else:
                    params_key = key
                params[params_key] = self.request.query_params.get(key);
        for key in self.GET_PARAMS_FOR_ICONTAINS_FILTER:
            if self.request.query_params.get(key):
                params[key + '__icontains'] = self.request.query_params.get(key);

    def get_queryset(self):
        """
        Filter the data with the couples attribute_name=value given in the GET parameters.
        If attribute_name is in GET_PARAMS_FOR_EQUALS_FILTER, the exact value will be searched in the corresponding
        attribute. If attribute_name is in GET_PARAMS_FOR_ICONTAINS_FILTER, it will select only the data whose the
        corresponding attribute contains this value.
        If a GET parameter is not part of these two arrays, its value will be ignored.
        """
        filter_params = {}
        self.__set_filter_params(filter_params)

        return Taxon.objects.filter(**filter_params)
