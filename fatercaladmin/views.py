from django.shortcuts import render
from django.contrib import admin
from django.db.models import F
from django.http import HttpResponse
from django.template import loader
from .models import Taxon
from .forms import TaxonChangeRef, TaxonChangeSup


# View for changing the validity, reference and/or superior of a taxon
def change_taxon_ref(request, id_taxon):
    taxon_to_change = Taxon.objects.get(id=id_taxon)
    # The user has finished changing the data  int the form and send it back
    if request.method == 'POST':
        form = TaxonChangeRef(request.POST)
        is_change_referent = False
        message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
        if form.is_valid():
            if form.cleaned_data['referent'] is not None:
                is_change_referent = True
                # taxon_to_change.update(id_ref=form.cleaned_data['referent'])
                if taxon_to_change.id == taxon_to_change.id_ref.id:
                    print(1)
                    # Taxon.objects.filter(id_ref=taxon_to_change).update(id_ref=form.cleaned_data['referent'])
                    # Taxon.objects.filter(id_sup=taxon_to_change).update(id_sup=form.cleaned_data['referent'])
                else:
                    if taxon_to_change.id == form.cleaned_data['referent'].id:
                        print(1)
    else:
        form = TaxonChangeRef()
        template = loader.get_template('fatercaladmin/change_taxon.html')
        context ={
            'taxon_to_change': taxon_to_change,
            'form': form,
        }
        return HttpResponse(template.render(context, request))


def change_taxon_sup(request, id_taxon):
    taxon_to_change = Taxon.objects.get(id=id_taxon)
    # The user has finished changing the data  int the form and send it back
    if request.method == 'POST':
        form = TaxonChangeSup(request.POST)
        is_change_superior = False
        message = "Le Taxon {} a bien été mis à jour".format(taxon_to_change.nom_complet)
        if form.is_valid():
            if form.cleaned_data[''] is not None:
                is_change_superior = True
                # taxon_to_change.update(id_ref=form.cleaned_data['referent'])
                if form.cleaned_data['taxon_superieur'] is None:
                    is_change_superior = True
                    # taxon_to_change.update(id_sup=form.cleaned_data['taxon_superieur'])
                    print(1)
                return HttpResponse(message)
    else:
        form = TaxonChangeSup()
        template = loader.get_template('fatercaladmin/change_taxon.html')
        context ={
            'taxon_to_change': taxon_to_change,
            'form': form,
        }
        return HttpResponse(template.render(context, request))


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
