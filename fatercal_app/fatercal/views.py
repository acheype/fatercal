from django.http import Http404
from django.contrib import admin
from django.db.models import F, Q
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .forms import AllTaxon, TaxonChangeSup, SearchAdvanced, ChooseData, UploadFileCsv, \
    ChooseTaxonToUpdate, ChooseTaxonToInsert
from .function import constr_hierarchy_tree_adv_search, get_taxon_from_search, is_admin, update_taxon_from_taxref, \
    get_taxon_personal, get_sample, get_taxons_for_sample, get_taxon_adv_search, change_ref_taxon, change_sup_taxon, \
    verify_and_save_sample, list_sample_for_map, get_taxon_from_search_taxref, get_taxref_update, get_taxref_insert, \
    insert_taxon_from_taxref, get_last_taxref_version, next_taxref_insert_page, delete_not_choose_taxref_insert
from .models import Taxon, TaxrefRang, TaxrefHabitat, TaxrefStatus, Vernaculaire
from .serializers import TaxonSerializer, TaxrefRangSerializer, TaxrefHabitatSerializer, TaxrefStatusSerializer, \
    VernaculaireSerializer
from .variable import list_hierarchy
from rest_framework import viewsets, generics
from rest_framework import permissions

import csv
import codecs
import datetime


class ValidSpecialFilter(admin.SimpleListFilter):
    """
    This filter will always return a subset
    of the instances in a Model, either filtering by the
    user choice or by a default value.
    """
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'filtre'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'valide'

    default_value = None

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ('valide', 'Valide'), ('synonyme', 'Synonyme'), ('no_superior', 'Aucun supérieur associé')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'valide':
            return queryset.filter(id=F('id_ref'))
        if self.value() == 'synonyme':
            return queryset.exclude(id=F('id_ref'))
        if self.value() == 'no_superior':
            return queryset.filter(Q(id_sup=None) & Q(id=F('id_ref')))


class AltitudeSpecialFilter(admin.SimpleListFilter):
    """
    This filter will always return a subset
    of the instances in a Model, either filtering by the
    user choice or by a default value.
    """
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Altitude'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'altitude'

    default_value = None

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ('max', 'Haut'), ('min', 'Bas')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'max':
            return queryset.order_by('altitude_max')
        if self.value() == 'min':
            return queryset.order_by('altitude_min')


@login_required()
def change_taxon_ref(request, id_taxon):
    """
    View for changing the validity, reference of a taxon
    :param request: an request object (see Django doc)
    :param id_taxon: The id specific to the taxon we want to change the referent.
    :return: an HttpResponse Object (see Django doc)
    """
    message, error = None, None
    taxon_to_change = Taxon.objects.get(id=id_taxon)
    if taxon_to_change == taxon_to_change.id_ref:
        # The user has finished changing the data in the form and send it back
        if request.method == 'POST':
            form = AllTaxon(request.POST)
            if form.is_valid():
                if taxon_to_change.id_ref == form.cleaned_data['taxon'].id_ref:
                    error = "Mettez un référent différent de celui existant."
                    template = loader.get_template('fatercal/change_taxon.html')
                else:
                    change_ref_taxon(taxon_to_change, form.cleaned_data)
                    message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
                    template = loader.get_template('fatercal/return_change_taxon.html')
            else:
                template = loader.get_template('fatercal/change_taxon.html')
                error = 'Veuillez choisir un taxon parmi ceux proposés.'

        else:
            template = loader.get_template('fatercal/change_taxon.html')
            error = None
    else:
        template = loader.get_template('fatercal/return_change_taxon.html')
        message = 'Le taxon {} n\'est pas un taxon valide. Retour a la page du taxon.' \
            .format(taxon_to_change.nom_complet)
    form = AllTaxon()
    context = {
        'form': form,
        'taxon_to_change': taxon_to_change,
        'message': message,
        'error': error,
        'user': request.user.__str__(),
    }
    return HttpResponse(template.render(context, request))


@login_required()
def change_taxon_sup(request, id_taxon):
    """
    View for changing the superior of a taxon
    :param request: an request object (see Django doc)
    :param id_taxon: The id specific to one taxon
    :return: an HttpResponse Object (see Django doc)
    """
    form, message, error = None, None, None
    taxon_to_change = Taxon.objects.get(id=id_taxon)
    # The user has finished changing the data in the form and send it back
    if taxon_to_change == taxon_to_change.id_ref:
        if request.method == 'POST':
            form = TaxonChangeSup(request.POST)
            message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
            if form.is_valid():
                if taxon_to_change != form.cleaned_data['taxon_superieur']:
                    template, error = change_sup_taxon(taxon_to_change, form.cleaned_data)
                else:
                    form = TaxonChangeSup()
                    template = loader.get_template('fatercal/change_taxon.html')
                    error = 'Ce taxon ne peut pas être son propre supérieur.'
            else:
                form = TaxonChangeSup()
                template = loader.get_template('fatercal/change_taxon.html')
                error = 'Veuillez choisir un taxon parmi ceux proposés.'
        else:
            form = TaxonChangeSup()
            template = loader.get_template('fatercal/change_taxon.html')
    else:
        template = loader.get_template('fatercal/return_change_taxon.html')
        message = 'Le taxon {} n\'est pas un taxon valide. Retour a la page du taxon.' \
                  ''.format(taxon_to_change.nom_complet)
    context = {
        'error': error,
        'form': form,
        'taxon_to_change': taxon_to_change,
        'message': message,
        'user': request.user.__str__(),
    }
    return HttpResponse(template.render(context, request))


@login_required()
def change_validity_to_valid(request, id_taxon):
    """
    View for changing a synonymous taxon to a valid one
    :param request: an request object (see Django doc)
    :param id_taxon: The id specific to one taxon
    :return: an HttpResponse Object (see Django doc)
    """

    taxon_to_change = Taxon.objects.get(id=id_taxon)
    # The user has finished changing the data  int the form and send it back
    if taxon_to_change != taxon_to_change.id_ref:
        taxon_to_change.id_ref = taxon_to_change
        taxon_to_change.save()
        template = loader.get_template('fatercal/return_change_taxon.html')
        message = 'Le taxon est devenu un taxon valide.'.format(taxon_to_change.nom_complet)
    else:
        template = loader.get_template('fatercal/return_change_taxon.html')
        message = 'Le taxon {} est déjà un taxon valide.'.format(taxon_to_change.nom_complet)
    context = {
        'taxon_to_change': taxon_to_change,
        'message': message,
        'user': request.user.__str__(),
    }
    return HttpResponse(template.render(context, request))


@login_required()
def advanced_search(request):
    """
    View for changing the superior of a taxon
    :param request: an request object (see Django doc)
    :return: an HttpResponse Object (see Django doc)
    """
    template = loader.get_template('fatercal/advanced_search/change_form.html')
    if request.method == 'POST':
        form = SearchAdvanced(request.POST)
        if form.is_valid():
            taxon = form.cleaned_data['taxon']
            auteur = form.cleaned_data['auteur']
            form = SearchAdvanced(initial={'auteur': auteur})
            hierarchy_tree, count_es = constr_hierarchy_tree_adv_search(taxon, auteur)
            context = {
                'list_taxon': hierarchy_tree,
                'auteur': auteur,
                'count_es': count_es,
                'taxon': taxon,
                'form': form,
            }
            return HttpResponse(template.render(context, request))
    template = loader.get_template('fatercal/advanced_search/change_form.html')
    form = SearchAdvanced()
    context = {
        'form': form,
        'count_es': -1
    }
    return HttpResponse(template.render(context, request))


@login_required()
def update_map(request):
    """
    Send an JSON response when the user choose a taxon
    :param request:
    :return: a JSON response
    """
    if request.method == 'GET':
        if bool(request.GET):
            if request.GET['taxon'] != '':
                taxon = Taxon.objects.get(id=request.GET['taxon'])
                if taxon is not None:
                    list_sample = list_sample_for_map(taxon)
                    return JsonResponse(list_sample, safe=False, content_type="application/json")
    return JsonResponse([], safe=False, content_type="application/json")


@login_required()
def map_sample(request):
    """
    A view for displaying the map with the sample of a taxon
    :param request: request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    template = loader.get_template('fatercal/prelevement/map_sample.html')
    context = {
        'form': AllTaxon(),
    }
    return HttpResponse(template.render(context, request))


@login_required()
def extract_taxon_taxref(request):
    """
    A view that streams a large CSV file. In this case the file in format
    for the organization taxref
    :param request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    if is_admin(request.user):
        param = None

        rows = (idx for idx in get_taxon_from_search_taxref(param))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fatercal_version_taxref' + \
                                          str(datetime.datetime.now()) + '.csv"'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response, delimiter=';')
        for row in rows:
            writer.writerow(row)
        return response
    raise Http404("This page doesn't exist.")


@login_required()
def extract_search_taxon_taxref(request):
    """
    A view that streams a large CSV file. In this case the file in format
    for the organization taxref
    :param request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    if is_admin(request.user):
        list_param = request.GET
        rows = (idx for idx in get_taxon_from_search_taxref(list_param))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fatercal_version_taxref_search' + \
                                          str(datetime.datetime.now()) + '.csv"'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response, delimiter=';')
        for row in rows:
            writer.writerow(row)
        return response
    raise Http404("This page doesn't exist.")


@login_required()
def choose_search_data(request):
    """
    View for choosing the field to export
    :param request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    list_param = None
    template = loader.get_template('fatercal/taxon/export_data_choose.html')
    if request.method == 'POST':
        form = ChooseData(request.POST)
        if form.is_valid():
            rows = (idx for idx in get_taxon_personal(form))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="fatercal_version_taxref' + \
                                              str(datetime.datetime.now()) + '.csv"'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response, delimiter=';')
            for row in rows:
                writer.writerow(row)
            return response
        else:
            form = ChooseData()
            template = loader.get_template('fatercal/change_taxon.html')
    else:
        list_param = request.GET
        if list_param is None:
            form = ChooseData()
        else:
            form = ChooseData(initial={key: value for (key, value) in list_param.items()})
    context = {
        'error': '',
        'form': form,
        'list_param': list_param,
        'user': request.user.__str__(),
    }
    return HttpResponse(template.render(context, request))


@login_required()
def extract_search_sample(request):
    """
    A view that streams a large CSV file. In this case the file in format
    for the organization taxref
    :param request: request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    #if is_admin(request.user):
    #try:
    list_param = request.GET
    rows = (idx for idx in get_sample(list_param))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fatercal_search_sample_' + \
                                      str(datetime.datetime.now()) + '.csv"'
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response, delimiter=';')
    for row in rows:
        writer.writerow(row)
    return response
    #except AttributeError:
    #    raise Http404("This page doesn't exist.")
    #else:
     #   raise Http404("This page doesn't exist")


@login_required()
def export_for_import_sample(request):
    """
    A simple csv file for future importation in the db
    :param request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    if is_admin(request.user):
        list_param = request.GET
        rows = (idx for idx in get_taxons_for_sample(list_param))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fatercal_export_import' + \
                                          str(datetime.datetime.now()) + '.csv"'
        writer = csv.writer(response, delimiter=';')
        for row in rows:
            writer.writerow(row)
        return response
    else:
        raise Http404("This page doesn't exist")


@login_required()
def add_sample_by_csv(request):
    """
    This page allow the user to import sample via a csv(or txt) file
    :param request: request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    if is_admin(request.user):
        template = loader.get_template('fatercal/prelevement/import_sample.html')
        message = ''
        if request.method == 'POST':
            form = UploadFileCsv(request.POST, request.FILES)
            if form.is_valid():
                filename = request.FILES['file'].name
                extension = filename[filename.rfind('.'):]
                csv_file = csv.DictReader(codecs.iterdecode(request.FILES['file'], 'latin-1'), delimiter=';')
                message = verify_and_save_sample(csv_file, extension)
            else:
                message = "Veuillez donnez le fichier d'importation."
        form = UploadFileCsv()
        context = {
            'message': message,
            'form': form,
        }
        return HttpResponse(template.render(context, request))
    else:
        raise Http404("This page doesn't exist")


@login_required()
def export_adv_search(request):
    """
    A view that streams a large CSV file. In this case the file in format
    for the organization taxref
    :param request: request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    if is_admin(request.user):
        try:
            taxon = request.GET.get("id")
            auteur = request.GET.get("auteur")
            rows = (idx for idx in get_taxon_adv_search(taxon, auteur))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="fatercal_adv_export_for_sample' + \
                                              str(datetime.datetime.now()) + '.csv"'
            writer = csv.writer(response, delimiter=';')
            for row in rows:
                writer.writerow(row)
            return response
        except AttributeError:
            raise Http404("This page doesn't exist.")
    else:
        raise Http404("This page doesn't exist.")


@login_required()
def update_from_taxref(request):
    """
    This page allow the user to choose the update from taxref to apply to Fatercal
    It takes the taxon with a cd_nom and search with taxref api if it has a similarity
    :param request: request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    if is_admin(request.user):
        if request.method == 'POST':
            form = ChooseTaxonToUpdate(request.POST, initial={'rang': None})
            template = loader.get_template('fatercal/taxon/update_taxon.html')
            if form.is_valid():
                taxref_version = get_last_taxref_version()
                data = form.cleaned_data
                update_taxon_from_taxref(data, taxref_version, request.user)
                error = False
            else:
                error = True
            context = {
                'error': error,
                'goal': 'update'
            }
        else:
            template = loader.get_template('fatercal/taxon/choose_taxon_update.html')
            empty, taxref_version, nb_taxon = get_taxref_update()
            if taxref_version['taxref_version__max'] is not None:
                form = ChooseTaxonToUpdate(
                    initial={
                        'taxref_version': int(taxref_version['taxref_version__max']),
                        'time': datetime.datetime.now()
                    })
            else:
                form = None
            context = {
                'form': form,
                'empty': empty,
                'nb_taxon': nb_taxon,
            }
        return HttpResponse(template.render(context, request))
    else:
        raise Http404("This page doesn't exist")


@login_required()
def insert_from_taxref(request):
    """
    This page allow the user to choose the taxon to insert from taxref
    If it doesn't exist in Fatercal and he exist in nc
    :param request: request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    if is_admin(request.user):
        if request.method == 'POST':
            form = ChooseTaxonToInsert(request.POST)
            template = loader.get_template('fatercal/taxon/choose_taxon_insert.html')
            if form.is_valid():
                error = False
                taxref_version = get_last_taxref_version()
                data = form.cleaned_data
                list_not_insert = insert_taxon_from_taxref(data, taxref_version, request.user)
                if data['count'] <= -1:
                    delete_not_choose_taxref_insert()
            else:
                list_not_insert = None
                error = True
            template, context = next_taxref_insert_page(form, error)
        else:
            rang = list_hierarchy[0]
            template = loader.get_template('fatercal/taxon/choose_taxon_insert.html')
            exist, exist_rang, nb_taxon, taxref_version = get_taxref_insert(rang)
            if taxref_version['taxref_version__max'] is not None:
                form = ChooseTaxonToInsert(
                    initial={
                        'rang': rang,
                        'taxref_version': int(taxref_version['taxref_version__max']),
                        'time': datetime.datetime.now(),
                        'count': 0
                    }
                )
            else:
                form = None
            rang = TaxrefRang.objects.get(rang=rang).lb_rang
            context = {
                'form': form,
                'exist': exist,
                'exist_rang': exist_rang,
                'rang': rang,
                'nb_taxon': nb_taxon
            }
        return HttpResponse(template.render(context, request))
    else:
        raise Http404("This page doesn't exist")


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

