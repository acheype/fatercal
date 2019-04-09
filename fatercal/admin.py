from django.contrib import admin
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from itertools import chain

from fatercal.views import ValidSpecialFilter, AltitudeSpecialFilter
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
        if not is_admin(request):
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

    # The field that will be showing to the user when we edit a synonymous
    fieldsets_edit_syn = (
        ('Taxonomie', {
            'fields': ('lb_nom', 'lb_auteur', 'nom_complet', 'valid', 'vernaculaires',
                       'referent', 'id_sup', 'rang', 'hierarchy')
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
            'fields': ('lb_nom', 'lb_auteur', 'nom_complet', 'valid', 'vernaculaires',
                       'syn', 'id_sup', 'rang', 'hierarchy')
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
            'fields': ('nc', 'habitat', 'grande_terre', 'iles_loyautee', 'autre',)
        }),
        ('Information complémentaires', {
            'classes': ('collapse',),
            'fields': ('remarque', 'sources', 'reference_description',)
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
        if obj.nom_complet is None or obj.nom_complet is '':
            if obj.lb_auteur is None:
                obj.nom_complet = obj.lb_nom
            else:
                obj.nom_complet = obj.lb_nom + ' ' + obj.lb_auteur
        super(TaxonModify, self).save_model(request, obj, form, change)
        # When a user want to create a new valid taxon to refer itself
        if obj.id_ref is None:
            obj.id_ref = obj
            obj.save()

    def change_taxon(self, obj):
        """
        Give the url path to change referent or superior
        :param obj: an Taxon object (see models.py)
        :return: a link to another page
        """
        if obj == obj.id_ref:
            return mark_safe("""<br/>
            <p><a href='/fatercal/change_ref/{}/'>Changez le référent</a></p>
            <p><a href="/fatercal/change_sup/{}/">Changez le supérieur</a></p>
            <br/>""".format(obj.id, obj.id))
        else:
            return mark_safe("<p>Vous ne pouvez pas changez le supérieur ou le référent de ce taxon.</p>")

    def vernaculaires(self, obj):
        """
        Return the list of vern's name of a taxon, and of its synonymous if its a valid taxon
        :param obj:
        :return:
        """
        list_vernaculaire = Vernaculaire.objects.filter(id_taxref=obj.id)
        string = "</br>"
        if obj.id == obj.id_ref_id:
            list_syn = Taxon.objects.filter(id_ref=obj.id).filter(~Q(id=obj.id))
            for syn in list_syn:
                list_vernaculaire_syn = Prelevement.objects.filter(id_taxref=syn.id)
                list_vernaculaire = list(chain(list_vernaculaire, list_vernaculaire_syn))
        if len(list_vernaculaire) == 0:
            string += "Aucun nom vernaculaire"
        else:
            for vern in list_vernaculaire:
                string += vern.nom_vern + "</br>"
        string += "</br><a href='/fatercal/vernaculaire/add?id_taxref={}'>Ajouter un Vernaculaire</a>".format(obj.id)
        return mark_safe(string)

    def prelevements(self, obj):
        """
        Return the list of sample of a taxon, and of its synonymous if its a valid taxon, in a synthetic html table
        :param obj: an Taxon object (see models.py)
        :return: an html table
        """
        board_prelevement = """<table><tr>
                                    <td><strong>Localisation</strong></td> <td><strong>Type enregistrement</strong></td>
                                    <td><strong>Date</strong></td><td> <strong>Nb taxon present</strong></td>
                                    <td><strong>Collection museum</strong></td> <td><strong>Type specimen </strong></td>
                                    <td><strong>Code specimen</strong></td> <td><strong>Altitude Minimum</strong></td>
                                    <td><strong>Altitude Maximum</strong></td> 
                                    <td><strong>Mode de collecte</strong></td> <td><strong>Toponyme</strong></td>
                                    <td><strong>Toponymie x</strong></td> <td><strong>Toponymie y</strong></td>
                                    <td><strong>Lien Modif</strong></td>
                                </tr>"""
        list_prelevement = Prelevement.objects.filter(id_taxref=obj.id)
        if obj.id == obj.id_ref_id:
            list_syn = Taxon.objects.filter(id_ref=obj.id).filter(~Q(id=obj.id))
            for syn in list_syn:
                list_prelevement_syn = Prelevement.objects.filter(id_taxref=syn.id)
                list_prelevement = list(chain(list_prelevement, list_prelevement_syn))
        for prelev in list_prelevement:
            board_prelevement += '''<tr>
                                    <td>{}</td>  <td>{}</td>  <td>{}</td>  <td>{}</td>  <td>{}</td>  <td>{}</td>
                                    <td>{}</td>  <td>{}</td>  <td>{}</td>  <td>{}</td>  <td>{}</td>  <td>{}</td>
                                    <td>{}</td> <td>{}</td>
                                    <td><a href='/fatercal/prelevement/{}/'>Modification</a></td>
                                    </tr>
                                ''' \
                .format(prelev.id_loc, prelev.type_enregistrement, prelev.date, prelev.nb_taxon_present,
                        prelev.collection_museum, prelev.type_specimen, prelev.code_specimen, prelev.altitude_min,
                        prelev.altitude_max, prelev.mode_de_collecte, prelev.toponyme, prelev.toponymie_x,
                        prelev.toponymie_y, get_recolteur(Recolteur, prelev), prelev.id_prelevement)
        board_prelevement += "</table></br><a href='/fatercal/prelevement/add?id_taxref={}'>Ajouter un Prelevement</a>"\
            .format(obj.id)
        return mark_safe(board_prelevement)

    def referent(self, obj):
        """
        Shown if the taxon is valid or not
        :param obj: an Taxon object (see models.py)
        :return: the validity in html tag
        """
        return mark_safe("""<a href='/fatercal/taxon/{}/'>{}</a> <br/> <br/> <a href="/fatercal/taxon_to_valid/{}">
                   Cliquer ici pour le passer en valide.</a>""".format(obj.id_ref_id, obj.id_ref.nom_complet, obj.id))

    def syn(self, obj):
        """
        Display the synonymous of the taxon
        :param obj: an Taxon object (see models.py)
        :return: The list of synonymous in html tag
        """
        list_syn = Taxon.objects.filter(id_ref=obj.id).filter(~Q(id=obj.id))
        if len(list_syn) != 0:
            string = "</br>"
            for syn in list_syn:
                string += "<a href='/fatercal/taxon/{}/'>{}</a><br/>".format(syn.id, syn.nom_complet)
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
            return mark_safe('<img src="/static/admin/img/icon-yes.gif" alt="True">')
        else:
            return mark_safe('<img src="/static/admin/img/icon-no.gif" alt="False">')

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
            str_taxon = '<li class="folder"><label><strong>{} :</strong> {} {}</label></li>' \
                .format(obj.rang, obj.lb_nom, obj.lb_auteur)
        else:
            str_taxon = '<li class="folder"><label><strong>{} :</strong><a href="/fatercal/taxon/{}/"> {} {}</a> ' \
                .format(obj.id_ref.rang, obj.id_ref_id, obj.id_ref.lb_nom, obj.lb_auteur)
        str_child = constr_hierarchy_tree_branch_child(list_child, nb)
        if str_child == '':
            return mark_safe('<ul class="tree"><br/>' + str_hierarchy_begin + str_taxon + str_hierarchy_end)
        else:
            str_hierarchy_end = str_child + '</ul></ul></li>'
            return mark_safe('<ul><br/>' + str_hierarchy_begin + str_taxon + str_hierarchy_end)

    @staticmethod
    def id(obj):
        return obj.id

    @staticmethod
    def id_ref_id(obj):
        return obj.id_ref_id

    @staticmethod
    def id_sup_id(obj):
        return obj.id_sup_id

    @staticmethod
    def old_db_id(obj):
        return obj.id_espece

    # list of file to use for style or javascript function
    class Media:
        css = {
            'all': ('admin/fatercal/taxon/css.css',)
        }

    # Override attribute in Model Admin
    vernaculaires.short_description = 'Vernaculaire'
    syn.short_description = 'Autre(s) combinaison(s) et/ou synonyme(s)'
    valid.short_description = 'Valide'
    hierarchy.short_description = 'Hiérarchie'


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
        'id_taxref',
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
        'id_taxref__lb_nom',
        'toponyme',
    )

    fieldsets = [
        ('Spécimen', {
            'fields': ('id_taxref', 'collection_museum', 'code_specimen', 'nb_taxon_present', 'type_specimen',)
        }),
        ('Informations', {
            'fields': ('type_enregistrement', 'plante_hote', 'mode_de_collecte', 'date',
                       'button_modal_date', 'information_complementaire')
        }),
        ('Localisation', {
            'fields': ('id_loc', 'toponyme', 'toponymie_x', 'toponymie_y', 'habitat',
                       'gps', 'altitude_min', 'altitude_max')
        }),
    ]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request):
            self.change_form_template = 'fatercal/change_form.html'
            return super(PrelevementModify, self).render_change_form(request, context, add, change, form_url, obj)
        else:
            return super(PrelevementModify, self).render_change_form(request, context, add, change, form_url, obj)

    # an url path to change referent or superior
    def button_modal_date(self, obj):
        return mark_safe('''
        Ces champs ne sont pas obligatoires ils vous aident juste à remplir le champ date au-dessus.<br><br>
        Date unique: <input type="date" oninput=Date_update('unique') id="date_1"><br><br>
        Période: <input type="date" id="date_periode_1" oninput=Date_update('periode')>
        <input type="date" id="date_periode_2" oninput=Date_update('periode')>
        ''')
    button_modal_date.short_description = 'Date Calendrier'

    # list of file to use for style or javascript function
    class Media:
        js = ('admin/fatercal/prelevement/prelev.js',)


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
        if not is_admin(request):
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
        if not is_admin(request):
            self.change_form_template = 'fatercal/change_form.html'
            return super(PlanteHoteModify, self).render_change_form(request, context, add, change, form_url, obj)
        else:
            return super(PlanteHoteModify, self).render_change_form(request, context, add, change, form_url, obj)


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

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request):
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
        'id_taxref__lb_nom',
    )

    fieldsets = [
        ('Informations', {
            'fields': ('iso639_3', 'language_name', 'language_name_fr', 'type')
        })
    ]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not is_admin(request):
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


# the list of model to show to the user for modification
admin.site.register(Taxon, TaxonModify)
admin.site.register(Localisation, LocalisationModify)
admin.site.register(Prelevement, PrelevementModify)
admin.site.register(Hote, HoteModify)
admin.site.register(PlanteHote, PlanteHoteModify)
admin.site.register(Vernaculaire, VernaculaireModify)
admin.site.register(Iso6393, Iso6393Modify)
admin.site.site_header = 'Fatercal'
admin.site.site_title = 'Fatercal'

# list signals for different models
post_save.connect(add_genre_to_name, sender=Taxon)
