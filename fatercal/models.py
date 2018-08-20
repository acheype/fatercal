# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models

from django.core.validators import RegexValidator


class DocsUses(models.Model):
    id_docuse = models.AutoField(primary_key=True)
    lb_docuse = models.TextField()

    class Meta:
        managed = True
        db_table = 'docs_uses'


class HabitatDetail(models.Model):
    id_taxref = models.ForeignKey('Taxon', db_column='id_taxref')
    nom = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'habitat_detail'


class Hote(models.Model):
    id_hote = models.ForeignKey('Taxon', db_column='id_hote', related_name='hote', verbose_name='Hote')
    id_parasite = models.ForeignKey('Taxon', db_column='id_parasite', related_name='parasite', verbose_name='Parasite')

    class Meta:
        managed = True
        db_table = 'hote'
        unique_together = (('id_hote', 'id_parasite'),)

    @staticmethod
    def autocomplete_search_fields():
        return 'id_hote__lb_nom', 'id_hote__lb_auteur',

    def __str__(self):

        return "{}".format(self.id_hote,)


class Iso6393(models.Model):
    iso639_3 = models.CharField(primary_key=True, max_length=3)
    language_name = models.CharField(max_length=50, blank=True, null=True)
    language_name_fr = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 'iso639-3'

    def __str__(self):

        return "{}".format(self.iso639_3,)


class Localitee(models.Model):
    id_localitee = models.AutoField(primary_key=True)
    localite = models.CharField(max_length=250, verbose_name='Localité')
    latitude = models.FloatField(blank=True, null=True,)
    longitude = models.FloatField(blank=True, null=True,)

    class Meta:
        managed = True
        db_table = 'localitee'

    def __str__(self):

        return self.localite


class PlanteHote(models.Model):
    id_plante_hote = models.AutoField(db_column='id_plante-hote', primary_key=True) # Field renamed remove characters.
    id_taxref = models.ForeignKey('Taxon', db_column='id_taxref', verbose_name="Taxon")
    famille = models.CharField(max_length=100, blank=True, null=True, verbose_name="Famille")
    genre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Genre")
    espece = models.CharField(max_length=100, blank=True, null=True, verbose_name="Espèce")

    def plante(self):
        """Return the name of the taxon"""
        return "{} {}".format(self.genre, self.espece)

    class Meta:
        managed = True
        db_table = 'plante_hote'

    def __str__(self):

        return "{} {}".format(self.genre, self.espece)


class Prelevement(models.Model):
    id_prelevement = models.AutoField(primary_key=True)
    id_localitee = models.ForeignKey(Localitee, db_column='id_localitee',
                                     blank=True, null=True, verbose_name='Localité')
    id_taxref = models.ForeignKey('Taxon', db_column='id_taxref', verbose_name='Taxon')
    type_enregistrement = models.ForeignKey('TypeEnregistrement', db_column='type_enregistrement',
                                            blank=True, null=True)
    date = models.CharField(max_length=10, blank=True, null=True,
                            validators=[
                                RegexValidator(
                                    regex=r"(^\d{4}$)|"
                                          r"(^\d{4}-(0[1-9]|1[0-2])$)|"
                                          r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)|"
                                          r"(^$)",
                                    message='La date doit être dans l\'une des formes suivantes: '
                                            '1850, 1850-12, 1850-12-01',
                                    code='invalid_username'
                                ),
                            ]
                            )
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
        managed = True
        db_table = 'prelevement'


class Recolteur(models.Model):
    id_prelevement = models.ForeignKey(Prelevement, db_column='id_prelevement', blank=True, null=True)
    lb_auteur = models.CharField(max_length=250, blank=True, null=True, verbose_name='Récolteurs')

    class Meta:
        managed = True
        db_table = 'recolteur'

    def __str__(self):
        return self.lb_auteur


class TypeEnregistrement(models.Model):
    lb_type = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.lb_type

    class Meta:
        managed = True
        db_table = 'type_enregistrement'


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
    iles_loyautee = models.NullBooleanField(verbose_name='Îles Loyauté')
    autre = models.NullBooleanField()
    territoire_fr = models.NullBooleanField()
    remarque = models.TextField(blank=True, null=True)
    sources = models.TextField(blank=True, null=True)
    id_espece = models.IntegerField(blank=True, null=True)
    reference_description = models.TextField(blank=True, null=True)

    def valide(self):
        """Return a boolean about whether or not it is a valid taxon"""
        return self == self.id_ref

    valide.boolean = True

    def __str__(self):
        if self.lb_auteur is not None:
            str_lb = str(self.lb_nom) + ' ' + str(self.lb_auteur)
        else:
            str_lb = str(self.lb_nom)
        if self != self.id_ref:
            str_lb += ' (Non Valide)'
        return str_lb

    def info(self):
        return '''<strong>Si vous voulez créer un nouveau taxon
        ne mettez rien dans référent et mettez
        un supérieur à votre nouveau taxon</strong>'''
    info.allow_tags = True

    @staticmethod
    def autocomplete_search_fields():
        return 'lb_nom', 'lb_auteur',

    class Meta:
        managed = True
        db_table = 'taxon'
        ordering = ['lb_nom']


class TaxrefHabitat(models.Model):
    habitat = models.SmallIntegerField(primary_key=True)
    lb_habitat = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'taxref_habitat'

    def __str__(self):
        return self.lb_habitat


class TaxrefRang(models.Model):
    rang = models.CharField(primary_key=True, max_length=4)
    lb_rang = models.CharField(max_length=100, verbose_name='Rang')

    def __str__(self):
        return self.lb_rang

    class Meta:
        managed = True
        db_table = 'taxref_rang'


class TaxrefStatus(models.Model):
    status = models.CharField(primary_key=True, max_length=4)
    lb_status = models.TextField()

    class Meta:
        managed = True
        db_table = 'taxref_status'

    def __str__(self):
        return self.lb_status


class Vernaculaire(models.Model):
    id_taxvern = models.AutoField(primary_key=True)
    id_taxref = models.ForeignKey(Taxon, db_column='id_taxref', verbose_name='Taxon')
    nom_vern = models.CharField(max_length=100, verbose_name='Nom Vernaculaire')
    pays = models.CharField(max_length=100, verbose_name='Pays d\'utilisation')
    iso639_3 = models.ForeignKey(Iso6393, db_column='iso639-3')

    class Meta:
        managed = True
        db_table = 'vernaculaire'

    def __str__(self):
        return self.nom_vern
