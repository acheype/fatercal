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
