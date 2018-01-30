from django import forms
from .models import Taxon
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField


class TaxonChangeRef(forms.Form):

    class Meta:
        model = Taxon

    referent = AutoCompleteSelectField("valid_and_syn", required=True, help_text=None)


class TaxonChangeSup(forms.Form):

    class Meta:
        model = Taxon

    taxon_superieur = AutoCompleteSelectField('valid', required=True, help_text=None)