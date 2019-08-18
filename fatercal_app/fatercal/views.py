from django.http import Http404
from django.contrib import admin
from django.db.models import F, Q
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import AllTaxon, TaxonChangeSup, SearchAdvanced, ChooseData, UploadFileCsv, \
    ChooseTaxonToUpdate
from .function import constr_hierarchy_tree_adv_search, get_taxon_from_search, is_admin,\
    get_taxon_personal, get_sample, get_taxons_for_sample, get_taxon_adv_search, change_ref_taxon, change_sup_taxon,\
    verify_and_save_sample, list_sample_for_map, get_taxon_from_search_taxref, get_taxref_update
from .models import Taxon

import csv
import json
import requests
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
    title = 'validité'

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
        return ('valide', 'Valide'), ('synonyme', 'Synonyme')

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
    if is_admin(request.user):
        try:
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
        except AttributeError:
            raise Http404("This page doesn't exist.")
    else:
        raise Http404("This page doesn't exist")


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
    It takes the taxon with a cd_nom and search with taxref api if it has
    :param request: request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    if is_admin(request.user):
        template = loader.get_template('fatercal/taxon/choose_taxon.html')
        list_dict_taxon, taxref_version = get_taxref_update()
        form = ChooseTaxonToUpdate(list_dict_taxon)
        context = {
            'form': form,
            'list_dict': list_dict_taxon
        }
        return HttpResponse(template.render(context, request))
    else:
        raise Http404("This page doesn't exist")
