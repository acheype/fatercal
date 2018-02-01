from django.contrib import admin
from django.db.models import Q
from django.db.models.signals import post_save

from fatercal.views import ValidSpecialFilter
from .models import Taxon, HabitatDetail, Localitee, Prelevement, Recolteur, Hote, PlanteHote, Vernaculaire, Iso6393
import nested_admin


class PlanteHoteObj(admin.StackedInline):
    """
        This Class will display the model of the table
        Hote to display all plant hote affected to the actual taxon selected
        by the user
    """
    model = PlanteHote
    # How many empty line it will display for creating new object
    extra = 1


class HoteParasiteObj(admin.StackedInline):
    """
        This Class will display the model of the table
        Hote to display all parasite affected to the actual taxon selected
        by the user
    """
    model = Hote
    # How many empty line it will display for creating new object
    fk_name = 'id_hote'
    verbose_name = "Parasite du taxon"
    verbose_name_plural = "Parasites du taxon"
    extra = 1


class HoteHoteObj(admin.StackedInline):
    """
        This Class will display the model of the table
        Hote to display all hote affected to the actual taxon selected
        by the user
    """
    model = Hote
    # How many empty line it will display for creating new object
    fk_name = 'id_parasite'
    verbose_name = "Hote du taxon"
    verbose_name_plural = "Hotes du taxon"
    extra = 1


class HabitatDetailObj(nested_admin.NestedTabularInline):
    """
    This Class will the model of the table
    HabitatDetail to display all the object affected to the actual taxon selected
    by the user
    """
    model = HabitatDetail
    # How many empty line it will display for creating new object
    extra = 1


# This class will be used to empack this inline in the  PrelevementObj nested_inline
class RecolteurObj(nested_admin.NestedStackedInline):
    """
        This Class will display the model of the table
        Recolteur to display all parasite affected to the actual prelevement selected
        by the user
    """
    model = Recolteur
    # How many empty line it will display for creating new object
    extra = 1


# The purpose of this class is to create new prelements for a taxon
class PrelevementObj(nested_admin.NestedStackedInline):
    """ This Class will display the model of the table Prelevement """
    model = Prelevement

    # The author who made the prelevement
    inlines = [RecolteurObj]
    # How many empty line it will display for creating a new object
    extra = 1


# This class serve to modify the admin look for the Model Taxon
class TaxonModify(nested_admin.NestedModelAdmin):
    """ This class will display the model Taxon for adding or modifying a taxon"""

    change_list_template = 'fatercal/taxon/change_list.html'

    # It will use the class define ealier to display all the object affected to the actual taxon
    inlines = (
        HoteHoteObj,
        HoteParasiteObj,
        PlanteHoteObj,
        HabitatDetailObj,
        PrelevementObj,
    )

    # a list of field that can't be modify
    readonly_fields = (
        'nom_complet',
        'hierarchy',
        'referent',
        'id',
        'id_sup_id',
        'id_ref_id',
        'cd_nom',
        'cd_ref',
        'cd_sup',
        'old_db_id'
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
        ValidSpecialFilter,
        'nc'
    )

    # The search field will be on these field to find a taxon
    search_fields = (
        'lb_nom',
        'lb_auteur',
    )

    # The field that will be showing to the user when we edit the object
    fieldsets_edit = (
        ('Taxonomie', {
            'fields': ('lb_nom', 'lb_auteur', 'nom_complet', 'referent', 'id_sup', 'rang', 'change_taxon', 'hierarchy')
        }),
        ('Statut et Habitat', {
            'fields': ('nc', 'habitat', 'grande_terre', 'iles_loyautee', 'autre',)
        }),
        ('Information complémentaires', {
            'classes': ('collapse',),
            'fields': ('remarque', 'sources', 'reference_description',)
        }),
        ('Identifiants', {
            'fields': ('id', 'id_ref_id', 'id_sup_id', 'cd_nom', 'cd_ref', 'cd_sup', 'old_db_id')
        })
    )

    # The field that will be showing to the user when we add a new object
    fieldsets_add = (
        ('Taxonomie', {
            'fields': ('lb_nom', 'lb_auteur', 'id_ref', 'id_sup', 'rang', 'info')
        }),
        ('Statut et Habitat', {
            'fields': ('nc', 'habitat', 'grande_terre', 'iles_loyautee', 'autre',)
        }),
        ('Information complémentaires', {
            'classes': ('collapse',),
            'fields': ('remarque', 'sources', 'reference_description',)
        })
    )

    # Redefinition of the function to have a readonly only when whe modify the object
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('id_sup', 'id_ref', 'change_taxon',)
        else:
            return self.readonly_fields + ('info',)

    # Redefinition of the function to have different fieldsets when we edit or add a taxon
    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets_edit
        else:
            return self.fieldsets_add

    # redefinition of the method save_model
    def save_model(self, request, obj, form, change):
        obj.nom_complet = obj.lb_nom + ' ' + obj.lb_auteur
        super(TaxonModify, self).save_model(request, obj, form, change)
        # When a user want to create a new valid taxon to refer itself
        if obj.id_ref is None:
            obj.id_ref = obj
            obj.save()

    # an url path to change referent or superior
    def change_taxon(self, obj):
        if obj == obj.id_ref:
            return """<br/>
            <p><a href='/fatercal/change_ref/{}/'>Changez le référent</a></p>
            <p><a href="/fatercal/change_sup/{}/">Changez le supérieur</a></p>
            <br/>
            """.format(obj.id, obj.id)
        else:
            return "<p>Vous ne pouvez pas changez le supérieur ou le référent de ce taxon.</p>"

    change_taxon.allow_tags = True

    # show if the taxon is valid or not whith is referent or synonymous
    def referent(self, obj):
        if obj == obj.id_ref:
            list_syn = Taxon.objects.filter(id_ref=obj.id).filter(~Q(id=obj.id))
            if len(list_syn) != 0:
                string = """Le taxon est valide.<br/>Voici ses synonymes:<br/>"""
                for tup in list_syn:
                    string += "<a href='/fatercal/taxon/{}/'>{}</a><br/>".format(tup.id, tup.nom_complet)
            else:
                string = """Le taxon est valide mais n'a pas de synonymes connues"""
            return string

        else:
            return """Le taxon n'est pas un valide. <br/> Voici son référent: 
            <a href='/fatercal/taxon/{}/'>{}</a> <br/> <br/> <a href="/fatercal/taxon_to_valid/{}">
                   Cliquer ici pour le passer en valide.</a>""".format(obj.id_ref.id, obj.id_ref.nom_complet, obj.id)

    referent.allow_tags = True

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
                    str_hierarchy_begin = str_hierarchy_begin + '''<li><label class="tree_label" for="c{}">
                    <strong>{} : </strong></al><a href="/fatercal/taxon/{}/">{}</a>
                    </label><ul>'''.format(nb2, tup.rang, tup.id, tup)
                    str_hierarchy_end = '</li></ul>' + str_hierarchy_end
                    nb2 = nb2-1
            son = Taxon.objects.filter(id_sup=obj.id).order_by('rang')
            if len(son) > 0:
                rang = son[0].rang
                str_son = '<ul><li><label class="tree_label" for="c{}"/><strong>{} : </strong></label><ul>'.format(str(nb+1), rang)
                for tup in son:
                    if rang != tup.rang:
                        str_son = str_son + '''</ul></li><li class="folder"><label for="c{}">
                        <strong>{} : </strong></label><li><ul>
                        <a href="/fatercal/taxon/{}/">{}</a>'''.format(str(nb+1), tup.rang, tup.id, tup)
                        rang = tup.rang
                    else:
                        str_son = str_son + '<li><a href="/fatercal/taxon/{}/">{} {}</a></li>'.format(tup.id, tup.lb_nom, tup.lb_auteur)
                str_son = str_son+'</ul></ul></li>'
                str_hierarchy = '<ul><br/>' + str_hierarchy_begin+'''<li class="folder">
                <strong>{} : </strong>{} {}<ul>'''.format(obj.rang, obj.lb_nom, obj.lb_auteur)+str_son+'</ul></li>'+str_hierarchy_end
            else:
                str_hierarchy = '<ul class="tree"><br/>' + str_hierarchy_begin + '''<li class="folder">
                <label>{} : </label><a href="/fatercal/taxon/{}/">{} {}</a></li>'''.format(obj.rang, obj.id, obj.lb_nom, obj.lb_auteur) + str_hierarchy_end
            return str_hierarchy
        else:
            return "Il n'y a pas de hiérarchie pour ce taxon"
    hierarchy.allow_tags = True

    @staticmethod
    def id(obj):
        return obj.id

    @staticmethod
    def id_ref_id(obj):
        return obj.id_ref.id

    @staticmethod
    def id_sup_id(obj):
        return obj.id_sup.id

    @staticmethod
    def old_db_id(obj):
        return obj.id_espece

    # list of file to use for style or javascript function
    class Media:
        css = {
            'all': ('admin/fatercal/taxon/css.css',)
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
        'toponyme',
        'date',
    )

    list_filter = (
        'toponyme',
    )

    inlines = (RecolteurObj,)

    # The search field will be on these field to find a taxon
    search_fields = (
        'id_taxref__lb_nom',
        'toponyme',
    )

    fieldsets = [
        ('Spécimen', {
            'fields': ('id_taxref', 'collection_museum', 'code_specimen', 'nb_taxon_present', 'type_specimen',)
        }),
        ('Informations', {
            'fields': ('type_enregistrement', 'mode_de_collecte', 'date', 'information_complementaire')
        }),
        ('Localisation', {
            'fields': ('id_localitee', 'toponyme', 'toponymie_x', 'toponymie_y', 'altitude', 'old_x', 'old_y')
        }),
    ]


class HoteModify(admin.ModelAdmin):
    """ This class will display the model Taxon for adding or modifying hote nad parasite"""
    list_display = [
        'id_hote',
        'id_parasite'
    ]

    search_fields = (
        'id_hote__lb_nom',
        'id_parasite__lb_nom',
    )

    fieldsets = [
        ('Informations', {
            'fields': ('id_hote', 'id_parasite',)
        })
    ]


class PlanteHoteModify(admin.ModelAdmin):
    """ This class will display the model Taxon for adding or modifying a plante_hote"""
    list_display = [
        'plante',
        'id_taxref',
    ]

    search_fields = (
        'id_taxref__lb_nom',
        'genre',
        'espece',
    )

    fieldsets = [
        ('Informations', {
            'fields': ('id_taxref', 'famille', 'genre', 'espece')
        })
    ]


class VernaculaireModify(admin.ModelAdmin):
    """ This class will display the model Taxon for adding or modifying a vernaculaire object"""
    list_display = [
        'id_taxref',
        'nom_vern',
    ]

    search_fields = (
        'id_taxref__lb_nom',
    )

    fieldsets = [
        ('Informations', {
            'fields': ('id_taxref', 'nom_vern', 'pays', 'iso639_3')
        })
    ]


class Iso6393Modify(admin.ModelAdmin):
    """ This class will display the model Taxon for adding or modifying a iso6393"""
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('iso639_3',)
        else:
            return self.readonly_fields

    list_display = [
        'iso639_3',
        'language_name',
        'language_name_fr',
    ]

    search_fields = (
        'id_taxref__lb_nom',
    )

    fieldsets = [
        ('Informations', {
            'fields': ('iso639_3', 'language_name', 'language_name_fr', 'type')
        })
    ]


def add_genre_to_name(sender, instance, created, **kwargs):
        if created:
            if instance.rang.rang == "ES":
                if instance.id_sup is not None:
                    if instance.id_sup.rang.rang == "GN":
                        instance.lb_nom = "{} ".format(instance.id_sup.lb_nom) + instance.lb_nom
                    elif instance.id_sup.rang.rang == "SSGN":
                        instance.lb_nom = "{} ".format(instance.id_sup.id_sup.lb_nom) + instance.lb_nom
            elif instance.rang.rang == "SSES":
                if instance.id_sup is not None:
                    if instance.id_sup.rang.rang == "ES":
                        instance.lb_nom = "{} ".format(instance.id_sup.lb_nom) + instance.lb_nom
            if instance.lb_auteur is not None:
                instance.nom_complet = instance.lb_nom + " " +instance.lb_auteur
            else:
                instance.nom_complet = instance.lb_nom


# the list of model to show to the user for modification
admin.site.register(Taxon, TaxonModify)
admin.site.register(Localitee, LocaliteeModify)
admin.site.register(Prelevement, PrelevementModify)
admin.site.register(Hote, HoteModify)
admin.site.register(PlanteHote, PlanteHoteModify)
admin.site.register(Vernaculaire, VernaculaireModify)
admin.site.register(Iso6393, Iso6393Modify)
admin.site.site_header = 'Fatercal'
admin.site.site_title = 'Fatercal'

# list signals for different models
post_save.connect(add_genre_to_name, sender=Taxon)