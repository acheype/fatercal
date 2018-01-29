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
                'managed': True,
                'db_table': 'docs_uses',
            },
        ),
        migrations.CreateModel(
            name='HabitatDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100)),
            ],
            options={
                'managed': True,
                'db_table': 'habitat_detail',
            },
        ),
        migrations.CreateModel(
            name='Hote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'managed': True,
                'db_table': 'hote',
            },
        ),
        migrations.CreateModel(
            name='Iso6393',
            fields=[
                ('iso639_3', models.CharField(primary_key=True, serialize=False, max_length=3)),
                ('language_name', models.CharField(blank=True, null=True, max_length=50)),
                ('language_name_fr', models.CharField(blank=True, null=True, max_length=50)),
                ('type', models.CharField(max_length=1)),
            ],
            options={
                'managed': True,
                'db_table': 'iso639-3',
            },
        ),
        migrations.CreateModel(
            name='Localitee',
            fields=[
                ('id_localitee', models.AutoField(primary_key=True, serialize=False)),
                ('localite', models.CharField(verbose_name='Localité', max_length=250)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
            options={
                'managed': True,
                'db_table': 'localitee',
            },
        ),
        migrations.CreateModel(
            name='PlanteHote',
            fields=[
                ('id_plante_hote', models.AutoField(primary_key=True, serialize=False, db_column='id_plante-hote')),
                ('famille', models.CharField(blank=True, verbose_name='Famille', null=True, max_length=100)),
                ('genre', models.CharField(blank=True, verbose_name='Genre', null=True, max_length=100)),
                ('espece', models.CharField(blank=True, verbose_name='Espèce', null=True, max_length=100)),
            ],
            options={
                'managed': True,
                'db_table': 'plante_hote',
            },
        ),
        migrations.CreateModel(
            name='Prelevement',
            fields=[
                ('id_prelevement', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, validators=[django.core.validators.RegexValidator(message="La date doit être dans l'une des formes suivantes: 1850, 1850-12, 1850-12-01", code='invalid_username', regex='\n                                        (^\\d{4}$)|\n                                        (^\\d{4}-(0[1-9]|1[0-2])$)|\n                                        (^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\\d|2\\d|3[0-1])$)|\n                                        (^$)\n                                    ')], null=True, max_length=10)),
                ('nb_taxon_present', models.SmallIntegerField(blank=True, null=True)),
                ('collection_museum', models.CharField(blank=True, null=True, max_length=250)),
                ('type_specimen', models.CharField(blank=True, null=True, max_length=250)),
                ('code_specimen', models.BigIntegerField(blank=True, null=True)),
                ('altitude', models.BigIntegerField(blank=True, null=True)),
                ('mode_de_collecte', models.CharField(blank=True, null=True, max_length=250)),
                ('toponyme', models.CharField(blank=True, null=True, max_length=250)),
                ('toponymie_x', models.FloatField(blank=True, null=True)),
                ('toponymie_y', models.FloatField(blank=True, null=True)),
                ('old_x', models.CharField(blank=True, verbose_name='Ancienne position x', null=True, max_length=250)),
                ('old_y', models.CharField(blank=True, verbose_name='Ancienne position y', null=True, max_length=250)),
                ('information_complementaire', models.TextField(blank=True, null=True)),
                ('id_localitee', models.ForeignKey(to='fatercal.Localitee', db_column='id_localitee', blank=True, verbose_name='Localité', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'prelevement',
            },
        ),
        migrations.CreateModel(
            name='Recolteur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('lb_auteur', models.CharField(blank=True, verbose_name='Récolteurs', null=True, max_length=250)),
                ('id_prelevement', models.ForeignKey(to='fatercal.Prelevement', db_column='id_prelevement', blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'recolteur',
            },
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('cd_nom', models.IntegerField(blank=True, null=True, unique=True)),
                ('cd_ref', models.IntegerField(blank=True, null=True)),
                ('cd_sup', models.IntegerField(blank=True, null=True)),
                ('lb_nom', models.CharField(verbose_name='Nom', max_length=250)),
                ('lb_auteur', models.CharField(blank=True, verbose_name='Auteur', null=True, max_length=250)),
                ('nom_complet', models.CharField(blank=True, null=True, max_length=250)),
                ('grande_terre', models.NullBooleanField()),
                ('iles_loyautee', models.NullBooleanField()),
                ('autre', models.NullBooleanField()),
                ('territoire_fr', models.NullBooleanField()),
                ('remarque', models.TextField(blank=True, null=True)),
                ('sources', models.TextField(blank=True, null=True)),
                ('id_espece', models.IntegerField(blank=True, null=True)),
                ('reference', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['lb_nom'],
                'managed': True,
                'db_table': 'taxon',
            },
        ),
        migrations.CreateModel(
            name='TaxrefHabitat',
            fields=[
                ('habitat', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('lb_habitat', models.CharField(max_length=100)),
            ],
            options={
                'managed': True,
                'db_table': 'taxref_habitat',
            },
        ),
        migrations.CreateModel(
            name='TaxrefRang',
            fields=[
                ('rang', models.CharField(primary_key=True, serialize=False, max_length=4)),
                ('lb_rang', models.CharField(verbose_name='Rang', max_length=100)),
            ],
            options={
                'managed': True,
                'db_table': 'taxref_rang',
            },
        ),
        migrations.CreateModel(
            name='TaxrefStatus',
            fields=[
                ('status', models.CharField(primary_key=True, serialize=False, max_length=4)),
                ('lb_status', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'taxref_status',
            },
        ),
        migrations.CreateModel(
            name='TypeEnregistrement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('lb_type', models.CharField(blank=True, null=True, max_length=250)),
            ],
            options={
                'managed': True,
                'db_table': 'type_enregistrement',
            },
        ),
        migrations.CreateModel(
            name='Vernaculaire',
            fields=[
                ('id_taxvern', models.AutoField(primary_key=True, serialize=False)),
                ('nom_vern', models.CharField(verbose_name='Nom Vernaculaire', max_length=100)),
                ('pays', models.CharField(verbose_name="Pays d'utilisation", max_length=100)),
                ('id_taxref', models.ForeignKey(to='fatercal.Taxon', db_column='id_taxref', verbose_name='Taxon')),
                ('iso639_3', models.ForeignKey(db_column='iso639-3', to='fatercal.Iso6393')),
            ],
            options={
                'managed': True,
                'db_table': 'vernaculaire',
            },
        ),
        migrations.AddField(
            model_name='taxon',
            name='habitat',
            field=models.ForeignKey(to='fatercal.TaxrefHabitat', db_column='habitat', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='taxon',
            name='id_ref',
            field=models.ForeignKey(related_name='id_ref+', to='fatercal.Taxon', db_column='id_ref', blank=True, verbose_name='Référent', null=True),
        ),
        migrations.AddField(
            model_name='taxon',
            name='id_sup',
            field=models.ForeignKey(related_name='id_sup+', to='fatercal.Taxon', db_column='id_sup', blank=True, verbose_name='Rang Supérieur', null=True),
        ),
        migrations.AddField(
            model_name='taxon',
            name='nc',
            field=models.ForeignKey(to='fatercal.TaxrefStatus', db_column='nc', blank=True, verbose_name='Statut', null=True),
        ),
        migrations.AddField(
            model_name='taxon',
            name='rang',
            field=models.ForeignKey(to='fatercal.TaxrefRang', db_column='rang', verbose_name='rang'),
        ),
        migrations.AddField(
            model_name='prelevement',
            name='id_taxref',
            field=models.ForeignKey(to='fatercal.Taxon', db_column='id_taxref', verbose_name='Taxon'),
        ),
        migrations.AddField(
            model_name='prelevement',
            name='type_enregistrement',
            field=models.ForeignKey(to='fatercal.TypeEnregistrement', db_column='type_enregistrement', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='plantehote',
            name='id_taxref',
            field=models.ForeignKey(to='fatercal.Taxon', db_column='id_taxref', verbose_name='Taxon'),
        ),
        migrations.AddField(
            model_name='hote',
            name='id_hote',
            field=models.ForeignKey(related_name='hote', to='fatercal.Taxon', db_column='id_hote', verbose_name='Hote'),
        ),
        migrations.AddField(
            model_name='hote',
            name='id_parasite',
            field=models.ForeignKey(related_name='parasite', to='fatercal.Taxon', db_column='id_parasite', verbose_name='Parasite'),
        ),
        migrations.AddField(
            model_name='habitatdetail',
            name='id_taxref',
            field=models.ForeignKey(db_column='id_taxref', to='fatercal.Taxon'),
        ),
        migrations.AlterUniqueTogether(
            name='hote',
            unique_together=set([('id_hote', 'id_parasite')]),
        ),
    ]
