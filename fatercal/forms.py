from django import forms
from .models import Taxon
from ajax_select.fields import AutoCompleteSelectField


class TaxonChangeRef(forms.Form):

    class Meta:
        model = Taxon

    referent = AutoCompleteSelectField("valid_and_syn", required=True, help_text=None)


class TaxonChangeSup(forms.Form):

    class Meta:
        model = Taxon

    taxon_superieur = AutoCompleteSelectField('valid', required=True, help_text=None)


class SearchAdvanced(forms.Form):
    search_term = forms.CharField(label='Nom taxonomique ou Auteur', max_length=40)
