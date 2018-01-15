from django.contrib import admin

from fatercaladmin.views import ValidSpecialFilter
from .models import Taxon, HabitatDetail, Localitee, Prelevement, PrelevementRecolteur
import nested_admin


class HabitatDetailObj(nested_admin.NestedTabularInline):
    """This Class will the model of the table
    HabitatDetail to display all the object affected to the actual taxon selected
    by the user
    """
    model = HabitatDetail
    # How many empty line it will display fro creating new object
    extra = 1


# This class will be used to empack this inline in the  PrelevementObj nested_inline
class PrelevementRecolteurObj(nested_admin.NestedStackedInline):

    model = PrelevementRecolteur
    # How many empty line it will display for creating new object
    extra = 1


# This class will be used only in Prelevement
class PrelevementRecolteurObjPrev(admin.StackedInline):
    """
    This Class will the model of the table
    PrelevementRecolteur to display all the object affected to a taxon
    """
    model = PrelevementRecolteur
    # How many empty line it will display for creating new object
    extra = 1


# The purpose of this class is to create new prelements for a taxon
class PrelevementObj(nested_admin.NestedStackedInline):
    """ This Class will the model of the table Prelevement """
    model = Prelevement

    # The author who made the prelevement
    inlines = [PrelevementRecolteurObj]
    # How many empty line it will display for creating a new object
    extra = 1


# This class serve to modify the admin look for the Model Taxon
class TaxonModify(nested_admin.NestedModelAdmin):
    """
    This class will display the model Taxon for modification
    """

    # It will use the class define ealier to display all the object affected to the actual taxon
    inlines = (
        HabitatDetailObj,
        PrelevementObj,
    )

    # a list of field that can't be modify
    readonly_fields = (
        'nom_complet',
        'hierarchy',
        'id',
        'id_sup_id',
        'id_ref_id',
        'cd_nom',
        'cd_ref',
        'cd_sup',
    )

    # A list of field displaying
    list_display = (
        'lb_nom',
        'lb_auteur',
        'rang',
        'valide',
    )

    # The list of filter the user can use
    list_filter = (
        'rang',
        ValidSpecialFilter
    )

    # The search field will be on these field to find a taxon
    search_fields = (
        'lb_nom',
        'lb_auteur',
    )

    # The field that will be showing to the user either or not it is alterable
    fieldsets = (
        ('Taxonomie', {
            'fields': ('lb_nom', 'lb_auteur', 'nom_complet', 'id_ref', 'id_sup', 'rang', 'hierarchy')
        }),
        ('Statut et Habitat', {
            'fields': ('nc', 'habitat', 'grande_terre', 'iles_loyautee', 'autre',)
        }),
        ('Information complémentaires', {
            'classes': ('collapse',),
            'fields': ('remarque', 'sources', 'reference',)
        }),
        ('Identifiants', {
            'fields': ('id', 'id_ref_id', 'id_sup_id', 'cd_nom', 'cd_ref', 'cd_sup',)
        })
    )

    # Redefinition of the function to have a readonly only when whe modify the object
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('id_sup', 'id_ref')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        obj.nom_complet = obj.lb_nom + ' ' + obj.lb_auteur
        super(TaxonModify, self).save_model(request, obj, form, change)

    def id(self, obj):
        return obj.id

    def id_ref_id(self, obj):
        return obj.id_ref.id

    def id_sup_id(self, obj):
        return obj.id_sup.id

    # This function will construct the hierarchy tree of the taxon
    def hierarchy(self, obj) :
        """ It will construct the hierarchy tree of the taxon """
        liste_hierarchy = []
        q = obj.id_sup
        liste_hierarchy.append(q)
        if obj.id == obj.id_ref.id:
            if q is not None:
                while q.id_sup is not None:
                    q = q.id_sup
                    liste_hierarchy.append(q)
                nb = len(liste_hierarchy)
            else:
                liste_hierarchy = None
                nb = 0
            str_hierarchy_begin = ''

            nb2 = nb-1
            str_hierarchy_end = '</ul>'
            if liste_hierarchy is not None:
                for tup in reversed(liste_hierarchy):
                    str_hierarchy_begin = str_hierarchy_begin + '<li><label class="tree_label" for="c{}"><strong>{} : </strong></al><a href="/admin/fatercaladmin/taxon/{}/">{}</a></label><ul>'.format(nb2, tup.rang, tup.id, tup)
                    str_hierarchy_end = '</li></ul>' + str_hierarchy_end
                    nb2 = nb2-1
            son = Taxon.objects.filter(id_sup=obj.id).order_by('rang')
            if len(son) > 0:
                rang = son[0].rang
                str_son = '<ul><li><label class="tree_label" for="c{}"/><strong>{} : </strong></label><ul>'.format(str(nb+1), rang)
                for tup in son:
                    if rang != tup.rang:
                        str_son = str_son + '</ul></li><li class="folder"><label for="c{}"><strong>{} : </strong></label><li><ul><a href="/admin/fatercaladmin/taxon/{}/">{}</a>'.format(str(nb+1), tup.rang, tup.id, tup)
                        rang = tup.rang
                    else:
                        str_son = str_son + '<li><a href="/admin/fatercaladmin/taxon/{}/">{} {}</a></li>'.format(tup.id, tup.lb_nom, tup.lb_auteur)
                str_son = str_son+'</ul></ul></li>'
                str_hierarchy = '<ul>Hierarchie du taxon' + str_hierarchy_begin+'<li class="folder"><strong>{} : </strong>{} {}<ul>'.format(obj.rang, obj.lb_nom, obj.lb_auteur)+str_son+'</ul></li>'+str_hierarchy_end
            else:
                str_hierarchy = '<ul class="tree">Hierarchie du taxon' + str_hierarchy_begin + '<li class="folder"><label>{} : </label><a href="/admin/fatercaladmin/taxon/{}/change">{} {}</a></li>'.format(obj.rang, obj.id, obj.lb_nom, obj.lb_auteur) + str_hierarchy_end
            return str_hierarchy
        else:
            return None
    hierarchy.allow_tags = True

    # list of file to use for style or javascript function
    class Media:
        css = {
            'all': ('admin/css.css',)
        }


class LocaliteeModify(admin.ModelAdmin):
    list_display = [
        'localite'
    ]

    fieldsets = [
        ('Informations', {
            'fields': ('localite', 'latitude', 'longitude')
        })
    ]


class PrelevementModify(admin.ModelAdmin):
    list_display = (
        'id_taxref',
        'date',
    )

    inlines = (PrelevementRecolteurObjPrev,)

    # Redefinition of the function to have a readonly only when whe modify the object
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('id_taxref',)
        return self.readonly_fields

    # The search field will be on these field to find a taxon
    search_fields = (
            'toponyme',
        )

    fieldsets = [
        ('Spécimen', {
            'fields': ('id_taxref', 'collection_museum', 'code_specimen', 'nb_taxon_present', 'type_specimen',)
        }),
        ('Informations', {
            'fields': ('type_enregistrement', 'mode_de_collecte', 'date',)
        }),
        ('Localisation', {
            'fields': ('id_localitee', 'toponyme', 'toponymie_x', 'toponymie_y', 'altitude', 'old_x', 'old_y')
        }),
    ]


admin.site.register(Taxon, TaxonModify)
admin.site.register(Localitee, LocaliteeModify)
admin.site.register(Prelevement, PrelevementModify)
