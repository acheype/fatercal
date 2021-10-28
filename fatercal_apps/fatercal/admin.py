from django.contrib import admin
# from django.contrib.admin import *

from django.db.models import Q
from django.urls import path, include, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from itertools import chain
from django.contrib.auth.models import Group, User
from django.templatetags.static import static

import datetime

from .views import ValidSpecialFilter, AltitudeSpecialFilter
from .models import Taxon, Localisation, Prelevement, Recolteur, Hote, PlanteHote, Vernaculaire, Iso6393
from .function import get_recolteur, constr_hierarchy_tree_branch_parents, constr_hierarchy_tree_branch_child, is_admin


# This class serve to modify or add a Parasite for the Model Taxon
class HoteParasiteObj(admin.StackedInline):
    """
        This Class will display the model of the table
        Hote to display all parasite affected to the actual taxon selected
        by the user
    """
    model = Hote
    fk_name = 'id_hote'
    verbose_name = "Parasite du taxon"
    verbose_name_plural = "Parasites du taxon"
    # How many empty line it will display for creating new object
    extra = 1


# This class serve to modify or add a Host for the Model Taxon
class HoteHoteObj(admin.StackedInline):
    """
    This Class will display the model of the table
    Hote to display all hote affected to the actual taxon selected
    by the user
    """
    model = Hote
    fk_name = 'id_parasite'
    verbose_name = "Hote du taxon"
    verbose_name_plural = "Hotes du taxon"
    # How many empty line it will display for creating new object
    extra = 1


# This class serve to modify or add an Harvester for the Model Prelevement
class RecolteurObj(admin.TabularInline):
    """
        This Class will display the model of the table
        Recolteur to display all parasite affected to the actual prelevement selected
        by the user
    """
    model = Recolteur
    # How many empty line it will display for creating new object
    extra = 1


# This class serve to modify the admin look for the Model Taxon
class TaxonModify(admin.ModelAdmin):
    """ This class will display the model Taxon for adding or modifying a taxon"""

    change_list_template = 'fatercal/taxon/change_list.html'

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request.user):
            self.change_form_template = 'fatercal/change_form.html'
            return super(TaxonModify, self).render_change_form(request, context, add, change, form_url, obj)
        else:
            return super(TaxonModify, self).render_change_form(request, context, add, change, form_url, obj)

    # It will use the class define ealier to display all the object affected to the actual taxon
    inlines = (
        HoteHoteObj,
        HoteParasiteObj,
    )

    # a list of field that can't be modify
    readonly_fields = (
        'nom_complet',
        'valid',
        'syn',
        'vernaculaires',
        'prelevements',
        'hierarchy',
        'referent',
        'id',
        'id_sup_id',  # TODO see if _id works...
        'id_ref_id',
        'cd_nom',
        'cd_ref',
        'cd_sup',
        'id_ancienne_bd'
    )

    # A list of field displaying
    list_display = (
        'lb_nom',
        'lb_auteur',
        'rang',
        'valid',
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

    # The field that will be showing to the user when we edit a synonymous
    fieldsets_edit_syn = (
        ('Taxonomie', {
            'fields': ('lb_nom', 'lb_auteur', 'nom_complet', 'valid', 'referent', 'vernaculaires', 'id_sup', 'rang',
                       'hierarchy')
        }),
        ('Statut et Habitat', {
            'fields': ('nc', 'habitat', 'grande_terre', 'iles_loyaute', 'autre',)
        }),
        ('Informations complémentaires', {
            'classes': ('collapse',),
            'fields': ('remarques', 'sources', 'reference_description',)
        }),
        ('Identifiants', {
            'fields': ('id', 'id_ref_id', 'id_sup_id', 'cd_nom', 'cd_ref', 'cd_sup', 'id_ancienne_bd')
        }),
        ('Modification', {
            'fields': ['change_taxon']
        }),
        ('Prélevements', {
            'fields': ['prelevements']
        })
    )

    # The field that will be showing to the user when we edit a valid taxon
    fieldsets_edit_valid = (
        ('Taxonomie', {
            'fields': ('lb_nom', 'lb_auteur', 'nom_complet', 'valid', 'syn', 'vernaculaires', 'id_sup', 'rang',
                       'hierarchy')
        }),
        ('Statut et Habitat', {
            'fields': ('nc', 'habitat', 'grande_terre', 'iles_loyaute', 'autre',)
        }),
        ('Informations complémentaires', {
            'classes': ('collapse',),
            'fields': ('remarques', 'sources', 'reference_description',)
        }),
        ('Identifiants', {
            'fields': ('id', 'id_ref_id', 'id_sup_id', 'cd_nom', 'cd_ref', 'cd_sup', 'id_ancienne_bd')
        }),
        ('Modification', {
            'fields': ['change_taxon']
        }),
        ('Prélevements', {
            'fields': ['prelevements']
        })
    )

    # The field that will be showing to the user when we add a new object
    fieldsets_add = (
        ('Taxonomie', {
            'fields': ('lb_nom', 'lb_auteur', 'id_ref', 'id_sup', 'rang', 'info')
        }),
        ('Statut et Habitat', {
            'fields': ('nc', 'habitat', 'grande_terre', 'iles_loyaute', 'autre',)
        }),
        ('Informations complémentaires', {
            'classes': ('collapse',),
            'fields': ('remarques', 'sources', 'reference_description',)
        })
    )

    # Redefinition of the function to have a readonly only when whe modify the object
    def get_readonly_fields(self, request, obj=None):
        """
        Return a list of readonly fields when a taxon is valid or not
        :param request: an request object (see Django doc)
        :param obj: an Taxon object (see models.py)
        :return: the readonly field
        """
        if obj:  # editing an existing object
            return self.readonly_fields + ('id_sup', 'id_ref', 'change_taxon',)
        else:
            return self.readonly_fields + ('info',)

    # Redefinition of the function to have different fieldsets when we edit or add a taxon
    def get_fieldsets(self, request, obj=None):
        """
        Change field when a taxon is valid or not
        :param request: an request object (see Django doc)
        :param obj: an Taxon object (see models.py)
        :return: the fieldsets
        """
        if obj:
            if obj.id == obj.id_ref_id:
                return self.fieldsets_edit_valid
            else:
                return self.fieldsets_edit_syn
        else:
            return self.fieldsets_add

    # redefinition of the method save_model
    def save_model(self, request, obj, form, change):
        """
        Add specific change when adding a new taxon
        :param request: an request object (see Django doc)
        :param obj: an Taxon object (see models.py)
        :param form: the used when creating the taxon
        :param change:
        :return: nothing
        """
        if obj.lb_auteur is None:
            obj.nom_complet = obj.lb_nom
        else:
            obj.nom_complet = obj.lb_nom + ' ' + obj.lb_auteur
        super(TaxonModify, self).save_model(request, obj, form, change)
        # when a user want to create a new valid taxon to refer itself
        if obj.id_ref is None:
            obj.id_ref = obj
            obj.save()
        if request.user is not None:
            obj.utilisateur = request.user.__str__()
        obj.source = 'Fatercal'
        obj.last_update = datetime.datetime.now()
        obj.save()

    def change_taxon(self, obj):
        """
        Give the url path to change referent or superior
        :param obj: an Taxon object (see models.py)
        :return: a link to another page
        """
        if obj == obj.id_ref:
            return mark_safe(
                f'''<br/><p><a href="{reverse('change_taxon_ref', args=[obj.id])}">Changez le référent</a></p>'''
                f'''<p><a href="{reverse('change_taxon_sup', args=[obj.id])}">Changez le supérieur</a></p>'''
            )
        else:
            return mark_safe("<p>Vous ne pouvez pas changez le supérieur ou le référent de ce taxon.</p>")

    def vernaculaires(self, obj):
        """
        Return the list of vern's name of a taxon, and of its synonymous if its a valid taxon
        :param obj:
        :return:
        """
        list_vernaculaire = Vernaculaire.objects.filter(id_taxon=obj.id)
        list_vernaculaire_syn = []
        string = ''
        if obj.id == obj.id_ref_id:
            list_syn = Taxon.objects.filter(id_ref=obj.id).filter(~Q(id=obj.id))
            for syn in list_syn:
                list_vernaculaire_syn = Vernaculaire.objects.filter(id_taxon=syn.id)
        if not list_vernaculaire and not list_vernaculaire_syn:
            string += "Aucun nom vernaculaire<br>"
        else:
            for vern in list_vernaculaire:
                string += f'''<a href="{reverse('admin:fatercal_vernaculaire_change', args=[vern.id])}">''' \
                        f'{vern.nom_vern}</a><br>'
            string += f'''<a href="{reverse('admin:fatercal_vernaculaire_add')}?id_taxon={obj.id}">''' \
                      '<i class="fas fa-plus-circle"></i> Ajouter un Vernaculaire</a><br>'
            if list_vernaculaire_syn:
                if list_vernaculaire:
                    string += '<br>'
                string += 'pour le(s) autre(s) combinaison(s) : <br>'
            for vern in list_vernaculaire_syn:
                string += f'''<a href="{reverse('admin:fatercal_vernaculaire_change', args=[vern.id])}">''' \
                        f'{vern.nom_vern}</a><br>'
        return mark_safe(string)

    def prelevements(self, obj):
        """
        Return the list of sample of a taxon, and of its synonymous if its a valid taxon, in a synthetic html table
        :param obj: an Taxon object (see models.py)
        :return: an html table
        """
        board_prelevement = '''<table><thead>
                                    <td>Localisation</td> <td>Type enregistrement</td>
                                    <td>Date</td><td> Nb taxon present</td>
                                    <td>Collection museum</td> <td>Type specimen </td>
                                    <td>Code specimen</td> <td>Altitude Minimum</td>
                                    <td>Altitude Maximum</td> 
                                    <td>Mode de collecte</td> <td>Toponyme</td>
                                    <td>Toponymie x</td> <td>Toponymie y</td>
                                    <td>Récoleurs</td>
                                    <td>Lien Modif</td>
                                </thead><tbody>'''
        list_prelevement = Prelevement.objects.filter(id_taxon=obj.id)
        if obj.id == obj.id_ref_id:
            list_syn = Taxon.objects.filter(id_ref=obj.id).filter(~Q(id=obj.id))
            for syn in list_syn:
                list_prelevement_syn = Prelevement.objects.filter(id_taxon=syn.id)
                list_prelevement = list(chain(list_prelevement, list_prelevement_syn))
        for prelev in list_prelevement:
            board_prelevement += f'''<tr>
                                        <td>{escape(prelev.localisation)}</td>
                                        <td>{prelev.type_enregistrement}</td>
                                        <td>{prelev.date}</td>
                                        <td>{prelev.nb_individus}</td>
                                        <td>{prelev.collection_museum}</td>
                                        <td>{prelev.type_specimen}</td>
                                        <td>{prelev.code_specimen}</td>
                                        <td>{prelev.altitude_min}</td>
                                        <td>{prelev.altitude_max}</td>
                                        <td>{prelev.mode_de_collecte}</td>
                                        <td>{prelev.toponyme}</td>
                                        <td>{prelev.toponymie_x}</td>
                                        <td>{prelev.toponymie_y}</td>
                                        <td>{get_recolteur(prelev)}</td>
                                        <td><a href='{reverse('admin:fatercal_prelevement_change', args=[prelev.id])}'>''' \
                                 'Modification</a></td>' \
                                 '</tr>'
        board_prelevement += f'''</tbody></table></br>''' \
                             f'''<a href="{reverse('admin:fatercal_prelevement_add')}?id_taxon={obj.id}">''' \
                             'Ajouter un Prélevement</a>'
        return mark_safe(board_prelevement)

    def referent(self, obj):
        """
        Shown if the taxon is valid or not
        :param obj: an Taxon object (see models.py)
        :return: the validity in html tag
        """
        return mark_safe(
            f'''<a href="{reverse('admin:fatercal_taxon_change', args=[obj.id_ref_id])}">{obj.id_ref.nom_complet}</a>'''
            f'''<br><br>'''
            f'''<a href="{reverse('taxon_to_valid', args=[obj.id])}">Cliquer ici pour le passer en valide.</a>'''
        );

    def syn(self, obj):
        """
        Display the synonymous of the taxon
        :param obj: an Taxon object (see models.py)
        :return: The list of synonymous in html tag
        """
        list_syn = Taxon.objects.filter(id_ref=obj.id).filter(~Q(id=obj.id))
        if list_syn:
            string = ''
            for syn in list_syn:
                string += f'''<a href="{reverse('admin:fatercal_taxon_change', args=[syn.id])}">''' \
                          f'{syn.nom_complet}</a><br/>'
        else:
            string = ""
        return mark_safe(string)

    def valid(self, obj):
        """
        Give an icon whether or not it is a valid taxon
        :param obj: an Taxon object (see models.py)
        :return: an image
        """
        if obj.id == obj.id_ref_id:
            return mark_safe(f'''<img src="{static('admin/img/icon-yes.gif')}" alt="True">''')
        else:
            return mark_safe(f'''<img src="{static('admin/img/icon-no.gif')}" alt="False">''')

    # This function will construct the hierarchy tree of the taxon
    def hierarchy(self, obj):
        """
        We verify the construction is for a taxon or synonymous
        :param obj: an Taxon object (see models.py)
        :return: an html tree
        """
        if obj.id == obj.id_ref_id:
            list_hierarchy, nb = obj.get_hierarchy()
            list_child = Taxon.objects.filter(id_sup=obj.id).order_by('rang')
            is_valid = True
        else:
            list_hierarchy, nb = obj.id_ref.get_hierarchy()
            list_child = Taxon.objects.filter(id_sup=obj.id_ref).order_by('rang')
            is_valid = False
        str_hierarchy_begin, str_hierarchy_end = constr_hierarchy_tree_branch_parents(list_hierarchy)
        if is_valid:
            str_taxon = f'<li class="folder"><label>{obj.rang} :</label> {obj.lb_nom} {obj.lb_auteur}</li>'
        else:
            str_taxon = f'<li class="folder"><label>{obj.id_ref.rang} : ' \
                        f'''<a href="{reverse('admin:fatercal_taxon_change', args=[obj.id_ref_id])}">''' \
                        f'{obj.id_ref.lb_nom} {obj.id_ref.lb_auteur}</a>'''
        str_child = constr_hierarchy_tree_branch_child(list_child, nb)
        if str_child == '':
            return mark_safe('<ul class="tree"><br/>' + str_hierarchy_begin + str_taxon + str_hierarchy_end)
        else:
            str_hierarchy_end = str_child + '</ul></ul></li>'
            return mark_safe('<ul class="tree"><br/>' + str_hierarchy_begin + str_taxon + str_hierarchy_end)

    # list of file to use for style or javascript function
    class Media:
        css = {
            'all': ('fatercal/taxon/style.css', static('fontawesome_free/css/all.min.css'),)
        }

    # Override attribute in Model Admin
    vernaculaires.short_description = 'Vernaculaire'
    syn.short_description = 'Autre(s) combinaison(s) et/ou synonyme(s)'
    valid.short_description = 'Valide'
    hierarchy.short_description = 'Hiérarchie'
    prelevements.short_description = 'Liste des prélèvements'


class LocalisationModify(admin.ModelAdmin):
    list_display = [
        'nom'
    ]

    fieldsets = [
        ('Informations', {
            'fields': ('nom', 'id_sup', 'latitude', 'longitude', 'loc_type')
        })
    ]


class PrelevementModify(admin.ModelAdmin):
    change_list_template = 'fatercal/prelevement/change_list.html'

    readonly_fields = (
        'button_modal_date',
    )
    list_display = (
        'id_taxon',
        'toponyme',
        'altitude_min',
        'altitude_max',
        'date',
    )

    list_filter = (
        'toponyme',
        AltitudeSpecialFilter
    )

    inlines = (RecolteurObj,)

    # The search field will be on these field to find a taxon
    search_fields = (
        'id_taxon__lb_nom',
        'toponyme',
    )

    fieldsets = [
        ('Spécimen', {
            'fields': ('id_taxon', 'collection_museum', 'code_specimen', 'nb_individus', 'type_specimen',)
        }),
        ('Informations', {
            'fields': ('type_enregistrement', 'plante_hote', 'mode_de_collecte', 'date',
                       'button_modal_date', 'infos_compl')
        }),
        ('Localisation', {
            'fields': ('localisation', 'toponyme', 'toponymie_x', 'toponymie_y', 'habitat',
                       'gps', 'altitude_min', 'altitude_max')
        }),
    ]

    # redefinition of the method save_model
    def save_model(self, request, obj, form, change):
        """
        Add specific change when adding a new taxon
        :param request: an request object (see Django doc)
        :param obj: an Prelevement object (see models.py)
        :param form: the form used when creating the taxon
        :param change:
        :return: nothing
        """
        # When loc is given we take the loc and toponymie is not given, we take the localisation number from loc
        if obj.localisation is not None and (obj.toponymie_x is None and obj.toponymie_y is None):
            if obj.localisation.latitude is not None and obj.localisation.longitude:
                obj.toponymie_x = obj.localisation.latitude
                obj.toponymie_y = obj.localisation.longitude
        super(PrelevementModify, self).save_model(request, obj, form, change)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request.user):
            self.change_form_template = 'fatercal/change_form.html'
            return super(PrelevementModify, self).render_change_form(request, context, add, change, form_url, obj)
        else:
            return super(PrelevementModify, self).render_change_form(request, context, add, change, form_url, obj)

    # an url path to change referent or superior
    def button_modal_date(self, obj):
        return mark_safe(
            '''Ces champs ne sont pas obligatoires ils vous aident juste à remplir le champ date au-dessus.<br><br>
            Date unique: <input type="date" oninput=date_update('unique') id="date_1"><br><br>
            Période: <input type="date" id="date_periode_1" oninput=date_update('periode')>
            <input type="date" id="date_periode_2" oninput=date_update('periode')>'''
        )

    button_modal_date.short_description = 'Date Calendrier'

    # list of file to use for style or javascript function
    class Media:
        js = ('fatercal/prelevement/prelev.js',)


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

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request.user):
            self.change_form_template = 'fatercal/change_form.html'
            return super(HoteModify, self).render_change_form(request, context, add, change, form_url, obj)
        else:
            return super(HoteModify, self).render_change_form(request, context, add, change, form_url, obj)


class PlanteHoteModify(admin.ModelAdmin):
    """ This class will display the model Taxon for adding or modifying a plante_hote"""
    list_display = [
        'plante'
    ]

    search_fields = (
        'famille',
        'genre',
        'espece',
    )

    fieldsets = [
        ('Informations', {
            'fields': ('famille', 'genre', 'espece')
        })
    ]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request.user):
            self.change_form_template = 'fatercal/change_form.html'
            return super(PlanteHoteModify, self).render_change_form(request, context, add, change, form_url, obj)
        else:
            return super(PlanteHoteModify, self).render_change_form(request, context, add, change, form_url, obj)


class VernaculaireModify(admin.ModelAdmin):
    """ This class will display the model Taxon for adding or modifying a vernaculaire object"""
    list_display = [
        'id_taxon',
        'nom_vern',
    ]

    search_fields = (
        'id_taxon__lb_nom',
    )

    fieldsets = [
        ('Informations', {
            'fields': ('id_taxon', 'nom_vern', 'pays', 'iso639_3')
        })
    ]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request.user):
            self.change_form_template = 'fatercal/change_form.html'
            return super(VernaculaireModify, self).render_change_form(request, context, add, change, form_url, obj)
        else:
            return super(VernaculaireModify, self).render_change_form(request, context, add, change, form_url, obj)


class Iso6393Modify(admin.ModelAdmin):
    """ This class will display the model Taxon for adding or modifying a iso6393 """

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
        'id_taxon__lb_nom',
    )

    fieldsets = [
        ('Informations', {
            'fields': ('iso639_3', 'language_name', 'language_name_fr', 'type')
        })
    ]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request.user):
            self.change_form_template = 'fatercal/change_form.html'
            return super(Iso6393Modify, self).render_change_form(request, context, add, change, form_url, obj)
        else:
            return super(Iso6393Modify, self).render_change_form(request, context, add, change, form_url, obj)


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
            instance.nom_complet = instance.lb_nom + " " + instance.lb_auteur
        else:
            instance.nom_complet = instance.lb_nom


# This class serve to redefine all urls of django admin by removing the application name
class FatercalAdminSite(admin.AdminSite):
    site_header = 'Fatercal'
    site_title = 'Fatercal'

    # def __init__(self, *args, **kwargs):
    #     super(FatercalAdminSite, self).__init__(*args, **kwargs)
    #     self._registry.update(site._registry)  # PART

    def get_urls(self):
        urlpatterns = super().get_urls()
        for model, model_admin in self._registry.items():
            urlpatterns += [
                path('%s/' % (model._meta.model_name), include(model_admin.urls)),
            ]
        return urlpatterns


# list signals for different models
post_save.connect(add_genre_to_name, sender=Taxon)

# the list of model to show to the user for modification
# TODO adapt with autodiscovery solution presented at https://stackoverflow.com/questions/32612400/auto-register-django-auth-models-using-custom-admin-site
fatercal_admin = FatercalAdminSite(name='FatercalAdmin')
fatercal_admin.register(Taxon, TaxonModify)
fatercal_admin.register(Localisation, LocalisationModify)
fatercal_admin.register(Prelevement, PrelevementModify)
fatercal_admin.register(Hote, HoteModify)
fatercal_admin.register(PlanteHote, PlanteHoteModify)
fatercal_admin.register(Vernaculaire, VernaculaireModify)
fatercal_admin.register(Iso6393, Iso6393Modify)

# inline import fix a 'Module does not define class' error
# https://stackoverflow.com/questions/67760162/module-does-not-define-class-error-while-replacing-default-admin-site
from django.contrib.auth.admin import UserAdmin, GroupAdmin

fatercal_admin.register(Group, GroupAdmin)
fatercal_admin.register(User, UserAdmin)
