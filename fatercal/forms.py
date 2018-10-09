from django import forms
from .models import Taxon
from ajax_select.fields import AutoCompleteSelectField


class TaxonChangeRef(forms.Form):
    referent = AutoCompleteSelectField("valid_and_syn", required=True, help_text=None)

    class Meta:
        model = Taxon


class TaxonChangeSup(forms.Form):
    taxon_superieur = AutoCompleteSelectField('valid', required=True, help_text=None)

    class Meta:
        model = Taxon


class SearchAdvanced(forms.Form):
    par_auteur = forms.BooleanField(required=False)
    search_term = forms.CharField(required=False, label='Champ de recherche', max_length=40)


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
