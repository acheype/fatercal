from ajax_select import register, LookupChannel
from .models import Taxon
from django.db.models import F


@register('valid')
class ValidLookup(LookupChannel):

    model = Taxon

    def get_query(self, q, request):
        return self.model.objects.filter(lb_nom__istartswith=q, id=F('id_ref')).order_by('lb_nom')

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item


@register('valid_and_syn')
class ValidSynLookup(LookupChannel):

    model = Taxon

    def get_query(self, q, request):
        return self.model.objects.filter(lb_nom__istartswith=q).order_by('lb_nom')

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item
