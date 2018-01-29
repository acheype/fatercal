from django.contrib import admin
from django.db.models import F
from django.http import HttpResponse
from django.template import loader
from .models import Taxon
from .forms import TaxonChangeRef, TaxonChangeSup
import csv
from django.http import StreamingHttpResponse


class Echo(object):
    """ An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """ Write the value by returning it, instead of storing in a buffer. """
        return value


def get_info(tup):
    """
    This function get all information of superior
    and miscellaneous info
    """
    sup = tup.id_sup
    if sup is None:
        sup = tup
    list_sup = [sup]
    while sup.id_sup is not None:
        list_sup.append(sup.id_sup)
        sup = sup.id_sup
    if tup.rang.lb_rang != 'Règne':
        regne = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == 'Règne'), None)
    else:
        regne = tup.lb_nom
    if tup.rang.lb_rang != "Phylum/Embranchement":
        phylum = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == "Phylum/Embranchement"), None)
    else:
        phylum = tup.lb_nom
    if tup.rang.lb_rang != "Classe":
        classe = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == "Classe"), None)
    else:
        classe = tup.lb_nom
    if tup.rang.lb_rang != "Ordre":
        ordre = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == "Ordre"), None)
    else:
        ordre = tup.lb_nom
    if tup.rang.lb_rang != "Famille":
        famille = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == "Famille"), None)
    else:
        famille = tup.lb_nom
    if tup.habitat is None:
        habitat = None
    else:
        habitat = tup.habitat.habitat
    if tup.nc is None:
        nc = None
    else:
        nc = tup.nc.status
    return {
        'regne': regne,
        'phylum': phylum,
        'class': classe,
        'order': ordre,
        'famille': famille,
        'habitat': habitat,
        'nc': nc,
    }


def get_msg(tup):
    """
    This function aim to get a message for taxref if it's != or not
    :param tup: the object from the Taxon model
    :return a tupple:
    """
    if tup.cd_nom is None:
        return 'x', None, None, None
    elif (tup.id_ref != tup and tup.cd_ref == tup.id_ref.cd_nom) or (tup.id_ref == tup and tup.cd_ref != tup.id_ref.cd_nom):
        return None, None, None, 'x'
    elif tup.cd_ref != tup.id_ref.cd_nom:
        return None, 'x', None, None
    elif tup.cd_sup is not None:
        if tup.cd_sup != tup.id_sup.cd_nom:
            return None, None, 'x', None
    return (None, None, None, None)


def get_taxon():
    """
    This function get all Information needed from a taxon
    """

    list_not_proper = Taxon.objects.all()
    list_taxon = [(
        'REGNE', 'PHYLUM', 'CLASSE', 'ORDRE',
        'FAMILLE', 'GROUP1_INPN',	'GROUP2_INPN', 'ID_',
        'ID_REF', 'ID_SUP', 'CD_NOM', 'CD_TAXSUP', 'CD_SUP',
        'CD_REF', 'RANG', 'LB_NOM',	'LB_AUTEUR', 'NOM_COMPLET',
        'NOM_COMPLET_HTML', 'NOM_VALIDE', 'NOM_VERN',
        'NOM_VERN_ENG', 'HABITAT', 'NC', 'NOT IN TAXREF', 'CD_REF !=', 'CD_SUP !=', 'VALIDITY !=')
    ]
    for tup in list_not_proper:
        msg = get_msg(tup)
        if 'sp.' not in tup.lb_nom:
            if tup == tup.id_ref:
                if tup.id_sup is None:
                    id_sup = None
                else:
                    id_sup = tup.id_sup_id
                dict_taxon = get_info(tup)
                tupple = (dict_taxon['regne'], dict_taxon['phylum'], dict_taxon['class'],
                           dict_taxon['order'], dict_taxon['famille'], None, None, tup.id, tup.id_ref.id,
                           id_sup, tup.cd_nom, None, tup.cd_sup, tup.cd_ref, tup.rang.rang,
                           tup.lb_nom, tup.lb_auteur, tup.nom_complet, None, tup.lb_nom, None, None,
                           dict_taxon['habitat'], dict_taxon['nc']) + msg
                list_taxon.append(tupple)
            else:
                dict_taxon = get_info(tup.id_ref)
                tupple = (dict_taxon['regne'], dict_taxon['phylum'], dict_taxon['class'],
                          dict_taxon['order'], dict_taxon['famille'], None, None, tup.id, tup.id_ref.id,
                          None, tup.cd_nom, None, tup.cd_sup, tup.cd_ref, tup.rang.rang,
                          tup.lb_nom, tup.lb_auteur, tup.nom_complet, None, tup.id_ref.lb_nom, None, None, None, None) + msg
                list_taxon.append(tupple)

    return list_taxon


def extract_taxon_taxref(request):
    """
    A view that streams a large CSV file. In this case the file in format
    for the organization taxref
    """
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    if request.user.is_authenticated():
        rows = (idx for idx in get_taxon())
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer,  delimiter=';')
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="fatercal_version_taxref.csv"'
        return response


def change_taxon_ref(request, id_taxon):
    """
    View for changing the superior of a taxon
    """
    if request.user.is_authenticated():
        taxon_to_change = Taxon.objects.get(id=id_taxon)
        if taxon_to_change == taxon_to_change.id_ref:
            # The user has finished changing the data  int the form and send it back
            if request.method == 'POST':
                form = TaxonChangeRef(request.POST)
                message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
                if form.is_valid():
                    if form.cleaned_data['referent'] is not None:
                        # taxon_to_change.update(id_ref=form.cleaned_data['referent'])
                        if taxon_to_change.id == taxon_to_change.id_ref.id:
                            list_syn = Taxon.objects.filter(id_ref=taxon_to_change)
                            list_son = Taxon.objects.filter(id_sup=taxon_to_change)
                            for tup in list_son:
                                tup.id_sup = form.cleaned_data['referent']
                                tup.save()
                            for tup in list_syn:
                                tup.id_ref = form.cleaned_data['referent']
                                tup.save()
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
                context ={
                    'taxon_to_change': taxon_to_change,
                    'form': form,
                    'user': request.user.__str__(),
                }
                return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('fatercal/return_change_taxon.html')
            message = 'Le taxon {} n\'est pas un taxon valide. Retour a la page du taxon.'.format(taxon_to_change.nom_complet)
            context = {
                'taxon_to_change': taxon_to_change,
                'message': message,
                'user': request.user.__str__(),
            }
            return HttpResponse(template.render(context, request))


def change_taxon_sup(request, id_taxon):
    """
    View for changing the validity, reference of a taxon
    """
    if request.user.is_authenticated():
        taxon_to_change = Taxon.objects.get(id=id_taxon)
        # The user has finished changing the data  int the form and send it back
        if taxon_to_change == taxon_to_change.id_ref:
            if request.method == 'POST':
                form = TaxonChangeSup(request.POST)
                is_change_superior = False
                message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
                if form.is_valid():
                    if form.cleaned_data['taxon_superieur'] is not None:
                        taxon_to_change.id_sup = form.cleaned_data['taxon_superieur']
                        taxon_to_change.save()
                    template = loader.get_template('fatercal/return_change_taxon.html')
                    context = {
                        'taxon_to_change': taxon_to_change,
                        'message': message,
                        'user': request.user.__str__(),
                    }
                    return HttpResponse(template.render(context, request))
            else:
                form = TaxonChangeSup()
                template = loader.get_template('fatercal/change_taxon.html')
                context ={
                    'taxon_to_change': taxon_to_change,
                    'form': form,
                    'user': request.user.__str__(),
                }
                return HttpResponse(template.render(context, request))
        else:
            return HttpResponse('Le taxon {} n\'est pas un valide. Retour a la page du taxon.'.format(taxon_to_change.nom_complet))


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
