# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DashboardUserdashboardmodule(models.Model):
    title = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    app_label = models.CharField(max_length=255, blank=True, null=True)
    user = models.IntegerField()
    column = models.IntegerField()
    order = models.IntegerField()
    settings = models.TextField()
    children = models.TextField()
    collapsed = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'dashboard_userdashboardmodule'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DocsTaxref(models.Model):
    id_doc = models.AutoField(primary_key=True)
    id_taxon = models.ForeignKey('Taxon', db_column='id_taxon', blank=True, null=True)
    id_docuse = models.ForeignKey('DocsUses', db_column='id_docuse', blank=True, null=True)
    page = models.SmallIntegerField(blank=True, null=True)
    url = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'docs_taxref'


class DocsUses(models.Model):
    id_docuse = models.AutoField(primary_key=True)
    lb_docuse = models.TextField()

    class Meta:
        managed = False
        db_table = 'docs_uses'


class HabitatDetail(models.Model):
    id_taxref = models.ForeignKey('Taxon', db_column='id_taxref')
    nom = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'habitat_detail'

class Hote(models.Model):
    id_hote = models.ForeignKey('Taxon', db_column='id_hote', related_name='hote')
    id_parasite = models.ForeignKey('Taxon', db_column='id_parasite', related_name='parasite')

    class Meta:
        managed = False
        db_table = 'hote'
        unique_together = (('id_hote', 'id_parasite'),)

class Iso6393(models.Model):
    iso639_3 = models.CharField(primary_key=True, max_length=3)
    language_name = models.CharField(max_length=50, blank=True, null=True)
    language_name_fr = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'iso639-3'


class JetBookmark(models.Model):
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=255)
    user = models.IntegerField()
    date_add = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'jet_bookmark'


class JetPinnedapplication(models.Model):
    app_label = models.CharField(max_length=255)
    user = models.IntegerField()
    date_add = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'jet_pinnedapplication'


class Localitee(models.Model):
    id_localitee = models.AutoField(primary_key=True)
    localite = models.CharField(max_length=250, verbose_name='Localité')
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        managed = False
        db_table = 'localitee'

    def __str__(self):

        return self.localite


class PlanteHote(models.Model):
    id_plante_hote = models.AutoField(db_column='id_plante-hote', primary_key=True)  # Field renamed to remove unsuitable characters.
    id_taxref = models.ForeignKey('Taxon', db_column='id_taxref')
    famille = models.CharField(max_length=100, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    espece = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plante_hote'


class Prelevement(models.Model):
    id_prelevement = models.AutoField(primary_key=True)
    id_localitee = models.ForeignKey(Localitee, db_column='id_localitee', blank=True, null=True, verbose_name='Localité')
    id_taxref = models.ForeignKey('Taxon', db_column='id_taxref', verbose_name='Taxon')
    type_enregistrement = models.ForeignKey('PrelevementTypeEnregistrement', db_column='type_enregistrement',
                                            blank=True, null=True)
    date = models.CharField(max_length=10, blank=True, null=True)
    nb_taxon_present = models.SmallIntegerField(blank=True, null=True)
    collection_museum = models.CharField(max_length=250, blank=True, null=True)
    type_specimen = models.CharField(max_length=250, blank=True, null=True)
    code_specimen = models.BigIntegerField(blank=True, null=True)
    altitude = models.BigIntegerField(blank=True, null=True)
    mode_de_collecte = models.CharField(max_length=250, blank=True, null=True)
    toponyme = models.CharField(max_length=250, blank=True, null=True)
    toponymie_x = models.FloatField(blank=True, null=True)
    toponymie_y = models.FloatField(blank=True, null=True)
    old_x = models.CharField(max_length=250, blank=True, null=True, verbose_name='Ancienne position x')
    old_y = models.CharField(max_length=250, blank=True, null=True, verbose_name='Ancienne position y')
    information_complementaire = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.date is None:
            return self.id_taxref.__str__()
        else:
            return "{} {}".format(self.id_taxref.__str__(), self.date)

    class Meta:
        managed = False
        db_table = 'prelevement'


class PrelevementRecolteur(models.Model):
    id_prelevement = models.ForeignKey(Prelevement, db_column='id_prelevement', blank=True, null=True)
    lb_auteur = models.CharField(max_length=250, blank=True, null=True, verbose_name='Récolteurs')

    class Meta:
        managed = False
        db_table = 'prelevement_auteurs'

    def __str__(self):
        return self.lb_auteur


class PrelevementTypeEnregistrement(models.Model):
    lb_type = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.lb_type

    class Meta:
        managed = False
        db_table = 'prelevement_type_enregistrement'


class Taxon(models.Model):

    id_ref = models.ForeignKey('self', db_column='id_ref', blank=True, null=True,
                               related_name='id_ref+', verbose_name='Référent')
    id_sup = models.ForeignKey('self', db_column='id_sup', blank=True, null=True,
                               related_name='id_sup+',verbose_name='Rang Supérieur')
    cd_nom = models.IntegerField(unique=True, blank=True, null=True)
    cd_ref = models.IntegerField(blank=True, null=True)
    cd_sup = models.IntegerField(blank=True, null=True)
    lb_nom = models.CharField(max_length=250, verbose_name='Nom')
    lb_auteur = models.CharField(max_length=250, blank=True, null=True, verbose_name='Auteur')
    nom_complet = models.CharField(max_length=250, blank=True, null=True)
    rang = models.ForeignKey('TaxrefRang', db_column='rang', verbose_name='rang', )
    habitat = models.ForeignKey('TaxrefHabitat', db_column='habitat', blank=True, null=True)
    nc = models.ForeignKey('TaxrefStatus', db_column='nc', blank=True, null=True,
                           verbose_name='Statut')
    grande_terre = models.NullBooleanField()
    iles_loyautee = models.NullBooleanField()
    autre = models.NullBooleanField()
    territoire_fr = models.NullBooleanField()
    remarque = models.TextField(blank=True, null=True)
    sources = models.TextField(blank=True, null=True)
    id_espece = models.IntegerField(blank=True, null=True)
    reference = models.TextField(blank=True, null=True)

    def valide(self):
        """Return a boolean about whether or not it is a valid taxon"""
        return self.id == self.id_ref.id

    valide.boolean = True

    def __str__(self):
        if self.lb_auteur is not None:
            str_lb = str(self.lb_nom) + ' ' + str(self.lb_auteur)
        else:
            str_lb = str(self.lb_nom)
        return str_lb

    @staticmethod
    def autocomplete_search_fields():
        return 'lb_nom', 'lb_auteur',

    class Meta:
        managed = False
        db_table = 'taxon'
        ordering = ['-lb_nom']


class TaxrefHabitat(models.Model):
    habitat = models.SmallIntegerField(primary_key=True)
    lb_habitat = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'taxref_habitat'

    def __str__(self):
        return self.lb_habitat


class TaxrefRang(models.Model):
    rang = models.CharField(primary_key=True, max_length=4)
    lb_rang = models.CharField(max_length=100, verbose_name='Rang')

    def __str__(self):
        return self.lb_rang

    class Meta:
        managed = False
        db_table = 'taxref_rang'


class TaxrefStatus(models.Model):
    status = models.CharField(primary_key=True, max_length=4)
    lb_status = models.TextField()

    class Meta:
        managed = False
        db_table = 'taxref_status'

    def __str__(self):
        return self.lb_status


class Taxvern(models.Model):
    id_taxvern = models.AutoField(primary_key=True)
    id_taxref = models.ForeignKey(Taxon, db_column='id_taxref')
    nom_vern = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    iso639_3 = models.ForeignKey(Iso6393, db_column='iso639-3')

    class Meta:
        managed = False
        db_table = 'taxvern'
