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
            name='Localitee',
            fields=[
                ('id_localitee', models.AutoField(primary_key=True, serialize=False)),
                ('localite', models.CharField(verbose_name='Localité', max_length=250)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
            options={
                'db_table': 'localitee',
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
                ('date', models.CharField(max_length=10, blank=True, null=True, validators=[django.core.validators.RegexValidator(regex='\n                                        (^\\d{4}$)|\n                                        (^\\d{4}-(0[1-9]|1[0-2])$)|\n                                        (^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\\d|2\\d|3[0-1])$)|\n                                        (^$)\n                                    ', message="La date doit être dans l'une des formes suivantes: 1850, 1850-12, 1850-12-01", code='invalid_username')])),
                ('nb_taxon_present', models.SmallIntegerField(blank=True, null=True)),
                ('collection_museum', models.CharField(max_length=250, blank=True, null=True)),
                ('type_specimen', models.CharField(max_length=250, blank=True, null=True)),
                ('code_specimen', models.BigIntegerField(blank=True, null=True)),
                ('altitude', models.BigIntegerField(blank=True, null=True)),
                ('mode_de_collecte', models.CharField(max_length=250, blank=True, null=True)),
                ('toponyme', models.CharField(max_length=250, blank=True, null=True)),
                ('toponymie_x', models.FloatField(blank=True, null=True)),
                ('toponymie_y', models.FloatField(blank=True, null=True)),
                ('old_x', models.CharField(verbose_name='Ancienne position x', max_length=250, blank=True, null=True)),
                ('old_y', models.CharField(verbose_name='Ancienne position y', max_length=250, blank=True, null=True)),
                ('information_complementaire', models.TextField(blank=True, null=True)),
                ('id_localitee', models.ForeignKey(verbose_name='Localité', blank=True, null=True, db_column='id_localitee', to='fatercal.Localitee')),
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
                ('iles_loyautee', models.NullBooleanField()),
                ('autre', models.NullBooleanField()),
                ('territoire_fr', models.NullBooleanField()),
                ('remarque', models.TextField(blank=True, null=True)),
                ('sources', models.TextField(blank=True, null=True)),
                ('id_espece', models.IntegerField(blank=True, null=True)),
                ('reference', models.TextField(blank=True, null=True)),
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
            name='type_enregistrement',
            field=models.ForeignKey(blank=True, null=True, db_column='type_enregistrement', to='fatercal.TypeEnregistrement'),
        ),
        migrations.AddField(
            model_name='plantehote',
            name='id_taxref',
            field=models.ForeignKey(verbose_name='Taxon', db_column='id_taxref', to='fatercal.Taxon'),
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
