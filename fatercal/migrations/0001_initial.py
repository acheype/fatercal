# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocsUses',
            fields=[
                ('id_docuse', models.AutoField(primary_key=True, serialize=False)),
                ('lb_docuse', models.TextField()),
            ],
            options={
                'db_table': 'docs_uses',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='HabitatDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('nom', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'habitat_detail',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Hote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'db_table': 'hote',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Iso6393',
            fields=[
                ('iso639_3', models.CharField(primary_key=True, max_length=3, serialize=False)),
                ('language_name', models.CharField(max_length=50, blank=True, null=True)),
                ('language_name_fr', models.CharField(max_length=50, blank=True, null=True)),
                ('type', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'iso639-3',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Localisation',
            fields=[
                ('id_loc', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(verbose_name='Nom', max_length=250)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('id_sup', models.ForeignKey(verbose_name='Localisation Supérieur', blank=True, null=True, db_column='id_sup', to='fatercal.Localisation')),
            ],
            options={
                'db_table': 'localisation',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PlanteHote',
            fields=[
                ('id_plante_hote', models.AutoField(primary_key=True, serialize=False, db_column='id_plante-hote')),
                ('famille', models.CharField(verbose_name='Famille', max_length=100, blank=True, null=True)),
                ('genre', models.CharField(verbose_name='Genre', max_length=100, blank=True, null=True)),
                ('espece', models.CharField(verbose_name='Espèce', max_length=100, blank=True, null=True)),
            ],
            options={
                'db_table': 'plante_hote',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Prelevement',
            fields=[
                ('id_prelevement', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(max_length=23, blank=True, null=True, validators=[django.core.validators.RegexValidator(regex='(^\\d{4}$)|(^\\d{4}-(0[1-9]|1[0-2])$)|(^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\\d|2\\d|3[0-1])$)|(^$)|(^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\\d|2\\d|3[0-1])\\/\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\\d|2\\d|3[0-1])$)', message="La date doit être dans l'une des formes suivantes: 1850, 1850-12, 1850-12-01", code='invalid_username')])),
                ('nb_taxon_present', models.SmallIntegerField(verbose_name='Nombre Individu', blank=True, null=True)),
                ('collection_museum', models.CharField(max_length=250, blank=True, null=True)),
                ('type_specimen', models.CharField(max_length=250, blank=True, null=True)),
                ('code_specimen', models.CharField(max_length=250, blank=True, null=True)),
                ('altitude_min', models.BigIntegerField(verbose_name='Altitude Minimum', blank=True, null=True)),
                ('altitude_max', models.BigIntegerField(verbose_name='Altitude Maximum', blank=True, null=True)),
                ('mode_de_collecte', models.CharField(max_length=250, blank=True, null=True)),
                ('toponyme', models.CharField(max_length=250, blank=True, null=True)),
                ('toponymie_x', models.FloatField(blank=True, null=True)),
                ('toponymie_y', models.FloatField(blank=True, null=True)),
                ('gps', models.NullBooleanField(verbose_name='GPS')),
                ('information_complementaire', models.TextField(blank=True, null=True)),
                ('habitat', models.ForeignKey(verbose_name='Habitat', blank=True, null=True, db_column='id_habitat', to='fatercal.HabitatDetail')),
                ('id_loc', models.ForeignKey(verbose_name='Localisation', blank=True, null=True, db_column='id_loc', to='fatercal.Localisation')),
            ],
            options={
                'db_table': 'prelevement',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Recolteur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('lb_auteur', models.CharField(verbose_name='Récolteurs', max_length=250, blank=True, null=True)),
                ('id_prelevement', models.ForeignKey(blank=True, null=True, db_column='id_prelevement', to='fatercal.Prelevement')),
            ],
            options={
                'db_table': 'recolteur',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('cd_nom', models.IntegerField(unique=True, blank=True, null=True)),
                ('cd_ref', models.IntegerField(blank=True, null=True)),
                ('cd_sup', models.IntegerField(blank=True, null=True)),
                ('lb_nom', models.CharField(verbose_name='Nom', max_length=250)),
                ('lb_auteur', models.CharField(verbose_name='Auteur', max_length=250, blank=True, null=True)),
                ('nom_complet', models.CharField(max_length=250, blank=True, null=True)),
                ('grande_terre', models.NullBooleanField()),
                ('iles_loyautee', models.NullBooleanField(verbose_name='Îles Loyauté')),
                ('autre', models.NullBooleanField()),
                ('territoire_fr', models.NullBooleanField()),
                ('remarque', models.TextField(blank=True, null=True)),
                ('sources', models.TextField(blank=True, null=True)),
                ('id_espece', models.IntegerField(blank=True, null=True)),
                ('reference_description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'taxon',
                'ordering': ['lb_nom'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TaxrefHabitat',
            fields=[
                ('habitat', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('lb_habitat', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'taxref_habitat',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TaxrefRang',
            fields=[
                ('rang', models.CharField(primary_key=True, max_length=4, serialize=False)),
                ('lb_rang', models.CharField(verbose_name='Rang', max_length=100)),
            ],
            options={
                'db_table': 'taxref_rang',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TaxrefStatus',
            fields=[
                ('status', models.CharField(primary_key=True, max_length=4, serialize=False)),
                ('lb_status', models.TextField()),
            ],
            options={
                'db_table': 'taxref_status',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TypeEnregistrement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('lb_type', models.CharField(max_length=250, blank=True, null=True)),
            ],
            options={
                'db_table': 'type_enregistrement',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TypeLoc',
            fields=[
                ('id_type', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(verbose_name='Type', max_length=10)),
            ],
            options={
                'db_table': 'type_loc',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Vernaculaire',
            fields=[
                ('id_taxvern', models.AutoField(primary_key=True, serialize=False)),
                ('nom_vern', models.CharField(verbose_name='Nom Vernaculaire', max_length=100)),
                ('pays', models.CharField(verbose_name="Pays d'utilisation", max_length=100)),
                ('id_taxref', models.ForeignKey(verbose_name='Taxon', db_column='id_taxref', to='fatercal.Taxon')),
                ('iso639_3', models.ForeignKey(db_column='iso639-3', to='fatercal.Iso6393')),
            ],
            options={
                'db_table': 'vernaculaire',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='taxon',
            name='habitat',
            field=models.ForeignKey(blank=True, null=True, db_column='habitat', to='fatercal.TaxrefHabitat'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='id_ref',
            field=models.ForeignKey(verbose_name='Référent', blank=True, null=True, db_column='id_ref', related_name='id_ref+', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='id_sup',
            field=models.ForeignKey(verbose_name='Rang Supérieur', blank=True, null=True, db_column='id_sup', related_name='id_sup+', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='nc',
            field=models.ForeignKey(verbose_name='Statut', blank=True, null=True, db_column='nc', to='fatercal.TaxrefStatus'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='rang',
            field=models.ForeignKey(verbose_name='rang', db_column='rang', to='fatercal.TaxrefRang'),
        ),
        migrations.AddField(
            model_name='prelevement',
            name='id_taxref',
            field=models.ForeignKey(verbose_name='Taxon', db_column='id_taxref', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='prelevement',
            name='plante_hote',
            field=models.ForeignKey(verbose_name='Plante Hote', blank=True, null=True, db_column='id_plante_hote', to='fatercal.PlanteHote'),
        ),
        migrations.AddField(
            model_name='prelevement',
            name='type_enregistrement',
            field=models.ForeignKey(blank=True, null=True, db_column='type_enregistrement', to='fatercal.TypeEnregistrement'),
        ),
        migrations.AddField(
            model_name='localisation',
            name='loc_type',
            field=models.ForeignKey(verbose_name='Type', db_column='loc_type', to='fatercal.TypeLoc'),
        ),
        migrations.AddField(
            model_name='hote',
            name='id_hote',
            field=models.ForeignKey(verbose_name='Hote', db_column='id_hote', related_name='hote', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='hote',
            name='id_parasite',
            field=models.ForeignKey(verbose_name='Parasite', db_column='id_parasite', related_name='parasite', to='fatercal.Taxon'),
        ),
        migrations.AlterUniqueTogether(
            name='hote',
            unique_together=set([('id_hote', 'id_parasite')]),
        ),
    ]
