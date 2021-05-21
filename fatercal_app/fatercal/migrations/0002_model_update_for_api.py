# Generated by Django 2.2.20 on 2021-05-22 03:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fatercal', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taxon',
            old_name='taxrefversion',
            new_name='taxref_version',
        ),
        migrations.RenameField(
            model_name='taxrefupdate',
            old_name='taxrefversion',
            new_name='taxref_version',
        ),
        migrations.RenameField(
            model_name='taxon',
            old_name='iles_loyautee',
            new_name='iles_loyaute',
        ),
        migrations.RenameField(
            model_name='taxon',
            old_name='id_espece',
            new_name='id_ancienne_bd',
        ),
        migrations.RenameField(
            model_name='prelevement',
            old_name='id_taxref',
            new_name='id_taxon',
        ),
        migrations.RenameField(
            model_name='vernaculaire',
            old_name='id_taxref',
            new_name='id_taxon',
        ),
        migrations.AlterField(
            model_name='vernaculaire',
            name='id_taxon',
            field=models.ForeignKey(db_column='id_taxref', on_delete=django.db.models.deletion.DO_NOTHING, related_name='noms_vern', to='fatercal.Taxon', verbose_name='Taxon'),
        ),
        migrations.AlterField(
            model_name='plantehote',
            name='id_plante_hote',
            field=models.AutoField(db_column='id_plante_hote', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='prelevement',
            name='id_taxon',
            field=models.ForeignKey(db_column='id_taxon', on_delete=django.db.models.deletion.DO_NOTHING, to='fatercal.Taxon', verbose_name='Taxon'),
        ),
        migrations.AlterField(
            model_name='vernaculaire',
            name='id_taxon',
            field=models.ForeignKey(db_column='id_taxon', on_delete=django.db.models.deletion.DO_NOTHING, related_name='noms_vern', to='fatercal.Taxon', verbose_name='Taxon'),
        ),
        migrations.RenameField(
            model_name='taxon',
            old_name='remarque',
            new_name='remarques',
        ),
    ]