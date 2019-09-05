from django import forms
from django.utils.safestring import mark_safe
from django.db.models import Q, Max
from .models import Taxon, TaxrefUpdate
from ajax_select.fields import AutoCompleteSelectField


class AllTaxon(forms.Form):
    taxon = AutoCompleteSelectField("valid_and_syn", required=True, help_text=None)

    class Meta:
        model = Taxon


class TaxonChangeSup(forms.Form):
    taxon_superieur = AutoCompleteSelectField('valid', required=True, help_text=None)

    class Meta:
        model = Taxon


class SearchAdvanced(forms.Form):
    taxon = AutoCompleteSelectField('valid', required=False, help_text=None)
    auteur = forms.CharField(required=False, max_length=40)

    class Meta:
        model = Taxon


class ChooseData(forms.Form):
    q = forms.CharField(widget=forms.HiddenInput(), required=False, max_length=40)
    nc__status__exact = forms.CharField(widget=forms.HiddenInput(), required=False, max_length=40)
    rang__rang__exact = forms.CharField(widget=forms.HiddenInput(), required=False, max_length=40)
    valide = forms.CharField(widget=forms.HiddenInput(), required=False, max_length=40)
    id = forms.BooleanField(required=False, label='ID Fatercal')
    id_sup = forms.BooleanField(required=False, label='ID Supérieur')
    id_ref = forms.BooleanField(required=False, label='ID Reférent')
    name = forms.BooleanField(required=False, label='Nom')
    author = forms.BooleanField(required=False, label='Auteur')
    rank = forms.BooleanField(required=False, label='Rang')
    rank_sup = forms.BooleanField(required=False, label='Rang Supérieur')
    status = forms.BooleanField(required=False, label='Statut')
    habitat = forms.BooleanField(required=False, label='Habitat')
    grande_terre = forms.BooleanField(required=False, label='Grande Terre')
    loyalty_island = forms.BooleanField(required=False, label='îles Loyauté')
    other = forms.BooleanField(required=False, label='Autre')
    remark = forms.BooleanField(required=False, label='Remarque')
    source = forms.BooleanField(required=False, label='Sources')
    description_reference = forms.BooleanField(required=False, label='Reference description')


class UploadFileCsv(forms.Form):
    file = forms.FileField(required=True, label='Fichier d\'import')

class ChooseTaxonToUpdate(forms.Form):
    time = forms.DateTimeField(widget=forms.HiddenInput())
    taxrefversion = forms.IntegerField(widget=forms.HiddenInput())
    def __init__(self, *args, **kwargs):
        super(ChooseTaxonToUpdate, self).__init__(*args, **kwargs)
        taxref_version = TaxrefUpdate.objects.aggregate(Max('taxrefversion'))
        self.fields['choices'] = forms.ModelMultipleChoiceField(
            queryset=TaxrefUpdate.objects.filter(
                Q(taxrefversion=taxref_version['taxrefversion__max']) 
                & ~Q(taxon_id=None)
            ),
            required=False,
            widget=forms.CheckboxSelectMultiple)
