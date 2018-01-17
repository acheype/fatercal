# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocsUses',
            fields=[
                ('id_docuse', models.AutoField(serialize=False, primary_key=True)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
            ],
            options={
                'db_table': 'hote',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Iso6393',
            fields=[
                ('iso639_3', models.CharField(serialize=False, max_length=3, primary_key=True)),
                ('language_name', models.CharField(max_length=50, blank=True, null=True)),
                ('language_name_fr', models.CharField(max_length=50, blank=True, null=True)),
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
                ('id_localitee', models.AutoField(serialize=False, primary_key=True)),
                ('localite', models.CharField(max_length=250, verbose_name='Localité')),
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
                ('id_plante_hote', models.AutoField(serialize=False, db_column='id_plante-hote', primary_key=True)),
                ('famille', models.CharField(max_length=100, blank=True, null=True)),
                ('genre', models.CharField(max_length=100, blank=True, null=True)),
                ('espece', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'plante_hote',
            },
        ),
        migrations.CreateModel(
            name='Prelevement',
            fields=[
                ('id_prelevement', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.CharField(max_length=10, blank=True, null=True)),
                ('nb_taxon_present', models.SmallIntegerField(blank=True, null=True)),
                ('collection_museum', models.CharField(max_length=250, blank=True, null=True)),
                ('type_specimen', models.CharField(max_length=250, blank=True, null=True)),
                ('code_specimen', models.BigIntegerField(blank=True, null=True)),
                ('altitude', models.BigIntegerField(blank=True, null=True)),
                ('mode_de_collecte', models.CharField(max_length=250, blank=True, null=True)),
                ('toponyme', models.CharField(max_length=250, blank=True, null=True)),
                ('toponymie_x', models.FloatField(blank=True, null=True)),
                ('toponymie_y', models.FloatField(blank=True, null=True)),
                ('old_x', models.CharField(blank=True, max_length=250, verbose_name='Ancienne position x', null=True)),
                ('old_y', models.CharField(blank=True, max_length=250, verbose_name='Ancienne position y', null=True)),
                ('information_complementaire', models.TextField(blank=True, null=True)),
                ('id_localitee', models.ForeignKey(null=True, db_column='id_localitee', verbose_name='Localité', blank=True, to='fatercal.Localitee')),
            ],
            options={
                'managed': True,
                'db_table': 'prelevement',
            },
        ),
        migrations.CreateModel(
            name='PrelevementRecolteur',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('lb_auteur', models.CharField(blank=True, max_length=250, verbose_name='Récolteurs', null=True)),
                ('id_prelevement', models.ForeignKey(db_column='id_prelevement', null=True, blank=True, to='fatercal.Prelevement')),
            ],
            options={
                'managed': True,
                'db_table': 'prelevement_auteurs',
            },
        ),
        migrations.CreateModel(
            name='PrelevementTypeEnregistrement',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('lb_type', models.CharField(max_length=250, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'prelevement_type_enregistrement',
            },
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('cd_nom', models.IntegerField(blank=True, unique=True, null=True)),
                ('cd_ref', models.IntegerField(blank=True, null=True)),
                ('cd_sup', models.IntegerField(blank=True, null=True)),
                ('lb_nom', models.CharField(max_length=250, verbose_name='Nom')),
                ('lb_auteur', models.CharField(blank=True, max_length=250, verbose_name='Auteur', null=True)),
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
                'managed': True,
                'db_table': 'taxon',
                'ordering': ['-lb_nom'],
            },
        ),
        migrations.CreateModel(
            name='TaxrefHabitat',
            fields=[
                ('habitat', models.SmallIntegerField(serialize=False, primary_key=True)),
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
                ('rang', models.CharField(serialize=False, max_length=4, primary_key=True)),
                ('lb_rang', models.CharField(max_length=100, verbose_name='Rang')),
            ],
            options={
                'managed': True,
                'db_table': 'taxref_rang',
            },
        ),
        migrations.CreateModel(
            name='TaxrefStatus',
            fields=[
                ('status', models.CharField(serialize=False, max_length=4, primary_key=True)),
                ('lb_status', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'taxref_status',
            },
        ),
        migrations.CreateModel(
            name='Taxvern',
            fields=[
                ('id_taxvern', models.AutoField(serialize=False, primary_key=True)),
                ('nom_vern', models.CharField(max_length=100)),
                ('pays', models.CharField(max_length=100)),
                ('id_taxref', models.ForeignKey(to='fatercal.Taxon', db_column='id_taxref')),
                ('iso639_3', models.ForeignKey(to='fatercal.Iso6393', db_column='iso639-3')),
            ],
            options={
                'managed': True,
                'db_table': 'taxvern',
            },
        ),
        migrations.AddField(
            model_name='taxon',
            name='habitat',
            field=models.ForeignKey(db_column='habitat', null=True, blank=True, to='fatercal.TaxrefHabitat'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='id_ref',
            field=models.ForeignKey(null=True, db_column='id_ref', verbose_name='Référent', blank=True, related_name='id_ref+', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='id_sup',
            field=models.ForeignKey(null=True, db_column='id_sup', verbose_name='Rang Supérieur', blank=True, related_name='id_sup+', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='nc',
            field=models.ForeignKey(null=True, db_column='nc', verbose_name='Statut', blank=True, to='fatercal.TaxrefStatus'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='rang',
            field=models.ForeignKey(db_column='rang', verbose_name='rang', to='fatercal.TaxrefRang'),
        ),
        migrations.AddField(
            model_name='prelevement',
            name='id_taxref',
            field=models.ForeignKey(db_column='id_taxref', verbose_name='Taxon', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='prelevement',
            name='type_enregistrement',
            field=models.ForeignKey(db_column='type_enregistrement', null=True, blank=True, to='fatercal.PrelevementTypeEnregistrement'),
        ),
        migrations.AddField(
            model_name='plantehote',
            name='id_taxref',
            field=models.ForeignKey(to='fatercal.Taxon', db_column='id_taxref'),
        ),
        migrations.AddField(
            model_name='hote',
            name='id_hote',
            field=models.ForeignKey(db_column='id_hote', related_name='hote', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='hote',
            name='id_parasite',
            field=models.ForeignKey(db_column='id_parasite', related_name='parasite', to='fatercal.Taxon'),
        ),
        migrations.AddField(
            model_name='habitatdetail',
            name='id_taxref',
            field=models.ForeignKey(to='fatercal.Taxon', db_column='id_taxref'),
        ),
        migrations.AlterUniqueTogether(
            name='hote',
            unique_together=set([('id_hote', 'id_parasite')]),
        ),
    ]
