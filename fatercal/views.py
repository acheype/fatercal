from .models import *
from django.http import Http404
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from .forms import AllTaxon, TaxonChangeSup, SearchAdvanced, ChooseData, UploadFileCsv


import json
import csv
import codecs
import datetime
from .function import *


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
    View for changing the superior of a taxon
    :param request: an request object (see Django doc)
    :param id_taxon: The id specific to the taxon we want to change the referent.
    :return: an HttpResponse Object (see Django doc)
    """

    taxon_to_change = Taxon.objects.get(id=id_taxon)
    if taxon_to_change == taxon_to_change.id_ref:
        # The user has finished changing the data in the form and send it back
        if request.method == 'POST':
            form = AllTaxon(request.POST)
            message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
            if form.is_valid():
                list_syn = Taxon.objects.filter(id_ref=taxon_to_change)
                list_child = Taxon.objects.filter(id_sup=taxon_to_change)
                for child in list_child:
                    child.id_sup = form.cleaned_data['taxon']
                    child.save()
                for syn in list_syn:
                    syn.id_ref = form.cleaned_data['taxon']
                    syn.save()
                if form.cleaned_data['taxon'] != form.cleaned_data['taxon'].id_ref:
                    form.cleaned_data['taxon'].id_ref = form.cleaned_data['taxon']
                    form.cleaned_data['taxon'].id_sup = taxon_to_change.id_sup
                    form.cleaned_data['taxon'].save()
                taxon_to_change.id_ref = form.cleaned_data['taxon']
                taxon_to_change.id_sup = None
                taxon_to_change.save()
                template = loader.get_template('fatercal/return_change_taxon.html')
                context = {
                    'taxon_to_change': taxon_to_change,
                    'message': message,
                    'user': request.user.__str__(),
                }
                return HttpResponse(template.render(context, request))
            else:
                form = AllTaxon()
                template = loader.get_template('fatercal/change_taxon.html')
                context = {
                    'error': 'Veuillez choisir un taxon parmi ceux proposés.',
                    'taxon_to_change': taxon_to_change,
                    'form': form,
                    'user': request.user.__str__(),
                }
                return HttpResponse(template.render(context, request))
        else:
            form = AllTaxon()
            template = loader.get_template('fatercal/change_taxon.html')
            context = {
                'error': None,
                'taxon_to_change': taxon_to_change,
                'form': form,
                'user': request.user.__str__(),
            }
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('fatercal/return_change_taxon.html')
        message = 'Le taxon {} n\'est pas un taxon valide. Retour a la page du taxon.' \
            .format(taxon_to_change.nom_complet)
        context = {
            'taxon_to_change': taxon_to_change,
            'message': message,
            'user': request.user.__str__(),
        }
        return HttpResponse(template.render(context, request))


@login_required()
def change_taxon_sup(request, id_taxon):
    """
    View for changing the validity, reference of a taxon
    :param request: an request object (see Django doc)
    :param id_taxon: The id specific to one taxon
    :return: an HttpResponse Object (see Django doc)
    """

    taxon_to_change = Taxon.objects.get(id=id_taxon)
    # The user has finished changing the data in the form and send it back
    if taxon_to_change == taxon_to_change.id_ref:
        if request.method == 'POST':
            form = TaxonChangeSup(request.POST)
            message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
            if form.is_valid():
                if taxon_to_change != form.cleaned_data['taxon_superieur']:
                    taxon_to_change.id_sup = form.cleaned_data['taxon_superieur']
                    try:
                        taxon_to_change.clean()
                        error = ''
                        taxon_to_change.save()
                        template = loader.get_template('fatercal/return_change_taxon.html')
                        context = {
                            'error': error,
                            'taxon_to_change': taxon_to_change,
                            'message': message,
                            'user': request.user.__str__(),
                        }
                        return HttpResponse(template.render(context, request))
                    except ValidationError as e:
                        error = e.message
                        form = TaxonChangeSup()
                        template = loader.get_template('fatercal/change_taxon.html')
                        context = {
                            'error': error,
                            'taxon_to_change': taxon_to_change,
                            'form': form,
                            'user': request.user.__str__(),
                        }
                        return HttpResponse(template.render(context, request))
                else:
                    form = TaxonChangeSup()
                    template = loader.get_template('fatercal/change_taxon.html')
                    context = {
                        'error': 'Veuillez choisir un taxon autre que lui même.',
                        'taxon_to_change': taxon_to_change,
                        'form': form,
                        'user': request.user.__str__(),
                    }
                    return HttpResponse(template.render(context, request))
            else:
                form = TaxonChangeSup()
                template = loader.get_template('fatercal/change_taxon.html')
                context = {
                    'error': 'Veuillez choisir un taxon parmi ceux proposés.',
                    'taxon_to_change': taxon_to_change,
                    'form': form,
                    'user': request.user.__str__(),
                }
                return HttpResponse(template.render(context, request))
        else:
            form = TaxonChangeSup()
            template = loader.get_template('fatercal/change_taxon.html')
            context = {
                'taxon_to_change': taxon_to_change,
                'form': form,
                'user': request.user.__str__(),
            }
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('fatercal/return_change_taxon.html')
        message = 'Le taxon {} n\'est pas un taxon valide. Retour a la page du taxon.' \
                  ''.format(taxon_to_change.nom_complet)
        context = {
            'error': None,
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
        message = 'Le taxon est devenu un taxon valide.'.format(
            taxon_to_change.nom_complet)
        context = {
            'taxon_to_change': taxon_to_change,
            'message': message,
            'user': request.user.__str__(),
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('fatercal/return_change_taxon.html')
        message = 'Le taxon {} est déjà un taxon valide.'.format(
            taxon_to_change.nom_complet)
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
            hierarchy_tree, count_es = constr_hierarchy_tree_adv_search(Taxon, taxon, auteur)
            context = {
                'list_taxon': hierarchy_tree,
                'auteur': auteur,
                'count_es': count_es,
                'taxon': taxon,
                'form': form,
            }
            return HttpResponse(template.render(context, request))
        else:
            return get_form_advanced_search(SearchAdvanced, request)
    else:
        return get_form_advanced_search(SearchAdvanced, request)


@login_required()
def update_map(request):
    """
    Send an JSON response when the user choose a taxon
    :param request:
    :return: a JSON response
    """
    if request.method == 'GET':
        if request.GET['taxon'] == '':
            return HttpResponse(json.dumps(None), content_type="application/json")
        else:
            taxon = Taxon.objects.get(id=request.GET['taxon'])
            if taxon is None:
                return HttpResponse(json.dumps(None), content_type="application/json")
            else:
                list_sample = []
                queryset = Prelevement.objects.filter(id_taxref=taxon.id)
                if taxon.id == taxon.id_ref_id:
                    queryset_synonymous = Taxon.objects.filter(id_ref=taxon.id).filter(~Q(id=taxon.id))
                    for taxon in queryset_synonymous:
                        queryset_synonymous_sample = Prelevement.objects.filter(id_taxref=taxon.id)
                        for sample in queryset_synonymous_sample:
                            if sample.toponymie_x is not None and sample.toponymie_y is not None:
                                list_sample.append({
                                    'sample_id': sample.id_prelevement,
                                    'latitude': sample.toponymie_y,
                                    'longitude': sample.toponymie_x,
                                })
                for sample in queryset:
                    if sample.toponymie_x is not None and sample.toponymie_y is not None:
                        default_loc = False
                        if sample.type_enregistrement is None:
                            t_enre = None
                        else:
                            t_enre = sample.type_enregistrement.lb_type
                        if sample.id_loc is None:
                            loc = None
                        else:
                            loc = sample.id_loc.nom
                            if sample.toponymie_x == sample.id_loc.longitude and \
                                    sample.id_loc.latitude == sample.toponymie_y:
                                default_loc = True
                        list_sample.append({
                            'id': sample.id_prelevement,
                            'loc': loc,
                            'default_loc': default_loc,
                            'latitude': sample.toponymie_y,
                            'longitude': sample.toponymie_x,
                            't_enre': t_enre,
                            'date': sample.date,
                            'collection_museum': sample.collection_museum,
                        })
                return HttpResponse(json.dumps(list_sample), content_type="application/json")
    else:
        return HttpResponse(json.dumps(None), content_type="application/json")


@login_required()
def map_sample(request):
    """
    A view for displaying the map with each taxon with their sample
    :param request: request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    if request.method == 'POST':
        form = AllTaxon(request.POST)
        if form.is_valid():
            taxon = form.cleaned_data['taxon']
            list_sample = []
            queryset = Prelevement.objects.filter(id_taxref=taxon.id)
            for sample in queryset.iterator():
                list_sample.append({
                    'id': sample.id_prelevement,
                    'latitude': sample.toponymie_y,
                    'longitude': sample.toponymie_x
                })
            template = loader.get_template('fatercal/prelevement/map_sample.html')
            context = {
                'form': form,
                'list_sample': list_sample,
                'error': '',
            }
            return HttpResponse(template.render(context, request))
    else:
        form = AllTaxon()
        template = loader.get_template('fatercal/prelevement/map_sample.html')
        context = {
            'form': form,
            'list_sample': [],
            'error': '',
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
    if is_admin(request):
        param = None
        rows = (idx for idx in get_taxon_from_search(Taxon, param))
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
    if is_admin(request):
        try:
            nb = request.META.get('HTTP_REFERER').find('?')
            if nb != -1:
                param = request.META.get('HTTP_REFERER')[nb + 1:]
            else:
                param = None
            rows = (idx for idx in get_taxon_from_search(Taxon, param))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="fatercal_version_taxref_search' + \
                                              str(datetime.datetime.now()) + '.csv"'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response, delimiter=';')
            for row in rows:
                writer.writerow(row)
            return response
        except AttributeError:
            raise Http404("This page doesn't exist.")
    raise Http404("This page doesn't exist.")


def choose_search_data(request):
    """
    View for choosing the field to export
    :param request: an request object (see Django doc)
    :return: an HttpResponse object (see Django doc)
    """
    template = loader.get_template('fatercal/taxon/export_data_choose.html')
    if request.method == 'POST':
        form = ChooseData(request.POST)
        if form.is_valid():
            rows = (idx for idx in get_taxon_personal(Taxon, form))
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
            context = {
                'error': 'Veuillez choisir un taxon parmi ceux proposés.',
                'form': form,
                'user': request.user.__str__(),
            }
        return HttpResponse(template.render(context, request))
    try:
        nb = request.META.get('HTTP_REFERER').find('?')
        if nb != -1:
            param = request.META.get('HTTP_REFERER')[nb + 1:]
        else:
            param = None
        list_param = inspect_url_variable(param, params_search_taxon)
    except AttributeError:
        raise Http404("This page doesn't exist.")
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
    if is_admin(request):
        try:
            nb = request.META.get('HTTP_REFERER').find('?')
            if nb != -1:
                param = request.META.get('HTTP_REFERER')[nb + 1:]
            else:
                param = None
            rows = (idx for idx in get_sample(Prelevement, Recolteur, Taxon, param))
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
    if is_admin(request):
        nb = request.META.get('HTTP_REFERER').find('?')
        if nb != -1:
            param = request.META.get('HTTP_REFERER')[nb + 1:]
        else:
            param = None
        rows = (idx for idx in get_taxons_for_sample(param, Taxon))
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
    if is_admin(request):
        template = loader.get_template('fatercal/prelevement/import_sample.html')
        message = ''
        if request.method == 'POST':
            form = UploadFileCsv(request.POST, request.FILES)
            try:
                if form.is_valid():
                    filename = request.FILES['file'].name
                    extension = filename[filename.rfind('.'):]
                    valid_extensions = ['.csv', '.txt']
                    if extension in valid_extensions:
                        csv_file = csv.DictReader(codecs.iterdecode(request.FILES['file'], 'latin-1'), delimiter=';')
                        list_dict_sample = []
                        count = 1
                        for row in csv_file:
                            result = verify_sample(row, Taxon, TypeEnregistrement, count)
                            if result['good']:
                                result = construct_sample(row, Taxon, Prelevement, Localisation,
                                                          Recolteur, TypeLoc, TypeEnregistrement, HabitatDetail, count)
                                list_dict_sample.append(result)
                            else:
                                raise NotGoodSample(result['message'])
                            count += 1
                        save_all_sample(list_dict_sample)
                        message = 'Tous les prélèvements ont tous été importé.'
                    else:
                        raise ValidationError(u'Unsupported file extension.')
                else:
                    message = "Veuillez donnez le fichier d'importation."
            except ValidationError:
                message = "Le fichier n'est pas dans le bon format."
            except NotGoodSample as e:
                message = e.message
            except KeyError:
                message = "Le fichier n'a pas les bon nom de colonne ou une colonne est manquante."
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
    if is_admin(request):
        try:
            taxon = request.GET.get("id")
            auteur = request.GET.get("auteur")
            rows = (idx for idx in get_taxon_adv_search(Taxon, taxon, auteur))
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
