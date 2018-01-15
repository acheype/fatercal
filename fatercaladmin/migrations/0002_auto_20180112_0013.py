# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fatercaladmin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=80, unique=True)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.BooleanField()),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.BooleanField()),
                ('is_active', models.BooleanField()),
                ('date_joined', models.DateTimeField()),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DashboardUserdashboardmodule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('module', models.CharField(max_length=255)),
                ('app_label', models.CharField(max_length=255, blank=True, null=True)),
                ('user', models.IntegerField()),
                ('column', models.IntegerField()),
                ('order', models.IntegerField()),
                ('settings', models.TextField()),
                ('children', models.TextField()),
                ('collapsed', models.BooleanField()),
            ],
            options={
                'db_table': 'dashboard_userdashboardmodule',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('action_time', models.DateTimeField()),
                ('object_id', models.TextField(blank=True, null=True)),
                ('object_repr', models.CharField(max_length=200)),
                ('action_flag', models.SmallIntegerField()),
                ('change_message', models.TextField()),
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('session_key', models.CharField(primary_key=True, max_length=40, serialize=False)),
                ('session_data', models.TextField()),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_session',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DocsTaxref',
            fields=[
                ('id_doc', models.AutoField(primary_key=True, serialize=False)),
                ('page', models.SmallIntegerField(blank=True, null=True)),
                ('url', models.CharField(max_length=250, blank=True, null=True)),
            ],
            options={
                'db_table': 'docs_taxref',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='JetBookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('url', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=255)),
                ('user', models.IntegerField()),
                ('date_add', models.DateTimeField()),
            ],
            options={
                'db_table': 'jet_bookmark',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='JetPinnedapplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('app_label', models.CharField(max_length=255)),
                ('user', models.IntegerField()),
                ('date_add', models.DateTimeField()),
            ],
            options={
                'db_table': 'jet_pinnedapplication',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Prelevement',
            fields=[
                ('id_prelevement', models.AutoField(primary_key=True, serialize=False)),
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
                ('old_latitude', models.CharField(verbose_name='Ancienne Latitude', max_length=250, blank=True, null=True)),
                ('old_longitude', models.CharField(verbose_name='Ancienne Longitude', max_length=250, blank=True, null=True)),
                ('information_complementaire', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'prelevement',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PrelevementRecolteur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('lb_auteur', models.CharField(verbose_name='Récolteurs', max_length=250, blank=True, null=True)),
            ],
            options={
                'db_table': 'prelevement_auteurs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PrelevementTypeEnregistrement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('lb_type', models.CharField(max_length=250, blank=True, null=True)),
            ],
            options={
                'db_table': 'prelevement_type_enregistrement',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('id_sup', models.IntegerField(blank=True, null=True)),
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
                'ordering': ['-lb_nom'],
                'managed': False,
            },
        ),
        migrations.AlterModelTable(
            name='iso6393',
            table='iso639-3',
        ),
    ]
