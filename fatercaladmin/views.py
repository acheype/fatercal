from django.contrib import admin
from django.db.models import F
from django.http import HttpResponse
from django.template import loader
from .models import Taxon
from .forms import TaxonChangeRef, TaxonChangeSup


# View for changing the validity, reference and/or superior of a taxon
def change_taxon_ref(request, id_taxon):
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
                            template = loader.get_template('fatercaladmin/return_change_taxon.html')
                            context = {
                                'taxon_to_change': taxon_to_change,
                                'message': message,
                                'user': request.user.__str__(),
                            }
                            return HttpResponse(template.render(context, request))
            else:
                form = TaxonChangeRef()
                template = loader.get_template('fatercaladmin/change_taxon.html')
                context ={
                    'taxon_to_change': taxon_to_change,
                    'form': form,
                    'user': request.user.__str__(),
                }
                return HttpResponse(template.render(context, request))
        else:
            return HttpResponse(
                'Le taxon {} n\'est pas un valide. Retour a la page du taxon.'.format(taxon_to_change.nom_complet))


def change_taxon_sup(request, id_taxon):
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
                    template = loader.get_template('fatercaladmin/return_change_taxon.html')
                    context = {
                        'taxon_to_change': taxon_to_change,
                        'message': message,
                        'user': request.user.__str__(),
                    }
                    return HttpResponse(template.render(context, request))
            else:
                form = TaxonChangeSup()
                template = loader.get_template('fatercaladmin/change_taxon.html')
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
