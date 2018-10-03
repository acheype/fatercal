from django.http import Http404
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from .models import Taxon, Prelevement
from .forms import TaxonChangeRef, TaxonChangeSup, SearchAdvanced, ChooseData
import csv
import datetime
from django.http import StreamingHttpResponse
from .function import *


class Echo(object):
    """ An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """ Write the value by returning it, instead of storing in a buffer. """
        return value


@login_required()
def change_taxon_ref(request, id_taxon):
    """
    View for changing the superior of a taxon
    :param request: an request object (see Django doc)
    :param id_taxon: The id specific to one taxon
    :return: an HttpResponse Object (see Django doc)
    """

    taxon_to_change = Taxon.objects.get(id=id_taxon)
    if taxon_to_change == taxon_to_change.id_ref:
        # The user has finished changing the data  int the form and send it back
        if request.method == 'POST':
            form = TaxonChangeRef(request.POST)
            message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
            if form.is_valid():
                # taxon_to_change.update(id_ref=form.cleaned_data['referent'])
                list_syn = Taxon.objects.filter(id_ref=taxon_to_change)
                list_child = Taxon.objects.filter(id_sup=taxon_to_change)
                for child in list_child:
                    child.id_sup = form.cleaned_data['referent']
                    child.save()
                for syn in list_syn:
                    syn.id_ref = form.cleaned_data['referent']
                    syn.save()
                if form.cleaned_data['referent'] != form.cleaned_data['referent'].id_ref:
                    form.cleaned_data['referent'].id_ref = form.cleaned_data['referent']
                    form.cleaned_data['referent'].id_sup = taxon_to_change.id_sup
                    form.cleaned_data['referent'].save()
                taxon_to_change.id_ref = form.cleaned_data['referent']
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
                form = TaxonChangeRef()
                template = loader.get_template('fatercal/change_taxon.html')
                context = {
                    'error': 'Veuillez choisir un taxon parmi ceux proposés.',
                    'taxon_to_change': taxon_to_change,
                    'form': form,
                    'user': request.user.__str__(),
                }
                return HttpResponse(template.render(context, request))
        else:
            form = TaxonChangeRef()
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
    # The user has finished changing the data  int the form and send it back
    if taxon_to_change == taxon_to_change.id_ref:
        if request.method == 'POST':
            form = TaxonChangeSup(request.POST)
            message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
            if form.is_valid():
                if taxon_to_change != form.cleaned_data['taxon_superieur']:
                    taxon_to_change.id_sup = form.cleaned_data['taxon_superieur']
                    taxon_to_change.save()
                    template = loader.get_template('fatercal/return_change_taxon.html')
                    context = {
                        'error': None,
                        'taxon_to_change': taxon_to_change,
                        'message': message,
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
            auteur = form.cleaned_data['par_auteur']
            search_term = form.cleaned_data['search_term']
            form = SearchAdvanced(initial={'search_term': search_term, 'par_auteur': auteur})
            list_taxon, count_es = constr_hierarchy_tree_adv_search(Taxon, search_term, auteur)
            context = {
                'list_taxon': list_taxon,
                'count_es': count_es,
                'search_term': search_term,
                'form': form,
            }
            return HttpResponse(template.render(context, request))
        else:
            return get_form_advanced_search(SearchAdvanced, request)
    else:
        return get_form_advanced_search(SearchAdvanced, request)


@login_required()
def extract_taxon_taxref(request):
    """
    A view that streams a large CSV file. In this case the file in format
    for the organization taxref
    :param request: an request object (see Django doc)
    :return: a csv file
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    param = None
    rows = (idx for idx in get_taxon(Taxon, param))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="fatercal_version_taxref' + \
                                      str(datetime.datetime.now()) + '.csv"'
    return response


@login_required()
def extract_search_taxon_taxref(request):
    """
    A view that streams a large CSV file. In this case the file in format
    for the organization taxref
    :param request: an request object (see Django doc)
    :return: a csv file
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    try:
        nb = request.META.get('HTTP_REFERER').find('?')
        if nb != -1:
            param = request.META.get('HTTP_REFERER')[nb + 1:]
        else:
            param = None
        rows = (idx for idx in get_taxon(Taxon, param))
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer, delimiter=';')
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="fatercal_version_taxref_search' + \
                                          str(datetime.datetime.now()) + '.csv"'
        return response
    except AttributeError:
        raise Http404("This page doesn't exist.")


def choose_search_data(request):
    """
    View for choosing the field to export
    :param request: an request object (see Django doc)
    :return: the view for choosing the field to export or a csv
    """
    template = loader.get_template('fatercal/taxon/export_data_choose.html')
    if request.method == 'POST':
        form = ChooseData(request.POST)
        if form.is_valid():
            rows = (idx for idx in get_taxon_personal(Taxon, form))
            pseudo_buffer = Echo()
            writer = csv.writer(pseudo_buffer, delimiter=';')
            response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                             content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename="fatercal_version_taxref' + \
                                              str(datetime.datetime.now()) + '.csv"'
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
    :return: a csv file
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    try:
        nb = request.META.get('HTTP_REFERER').find('?')
        if nb != -1:
            param = request.META.get('HTTP_REFERER')[nb + 1:]
        else:
            param = None
        rows = (idx for idx in get_sample(Prelevement, param))
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer, delimiter=';')
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="fatercal_search_sample_' +\
                                          str(datetime.datetime.now()) + '.csv"'
        return response
    except AttributeError:
        raise Http404("This page doesn't exist.")


@login_required()
def export_for_import_sample(request):
    """
    A simple csv file for future export in the db
    :param request: an request object (see Django doc)
    :return: a csv file
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    nb = request.META.get('HTTP_REFERER').find('?')
    if nb != -1:
        param = request.META.get('HTTP_REFERER')[nb + 1:]
    else:
        param = None
    rows = (idx for idx in get_taxons_for_sample(param, Taxon))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="fatercal_export_import' + \
                                      str(datetime.datetime.now()) + '.csv"'
    return response


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
