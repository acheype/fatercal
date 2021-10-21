from ajax_select import register, LookupChannel
from django.urls import reverse

from .models import Taxon
from django.db.models import F


@register('valid')
class ValidLookup(LookupChannel):
    """
    A lookup to have all valid taxons
    """

    model = Taxon

    def get_query(self, q, request):
        return self.model.objects.filter(lb_nom__istartswith=q, id=F('id_ref')).order_by('lb_nom')

    def format_item_display(self, item):
        return f'''<span class='tag'><a href="{reverse('admin:fatercal_taxon_change', args=[item.id])}">{item}</a>''' \
               '</span>'


@register('valid_and_syn')
class ValidSynLookup(LookupChannel):
    """
        A lookup to have all valid and synonymous taxons
    """
    model = Taxon

    def get_query(self, q, request):
        return self.model.objects.filter(lb_nom__istartswith=q).order_by('lb_nom')

    def format_item_display(self, item):
        return f'''<span class='tag'><a href="{reverse('admin:fatercal_taxon_change', args=[item.id])}">{item}</a>''' \
               '</span>'
