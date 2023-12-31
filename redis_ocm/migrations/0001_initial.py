# Generated by Django 3.0.8 on 2023-10-05 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ET1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FK',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='M2M',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PT1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='RD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('last_accessed', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RedisTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('last_accessed', models.DateTimeField(null=True)),
            ],
            options={
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='PickleModel',
            fields=[
                ('redistest_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='redis_ocm.RedisTest')),
            ],
            bases=('redis_ocm.redistest',),
        ),
        migrations.CreateModel(
            name='RedisModel',
            fields=[
                ('redistest_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='redis_ocm.RedisTest')),
            ],
            bases=('redis_ocm.redistest',),
        ),
        migrations.CreateModel(
            name='FKP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='redis_ocm.FK')),
                ('m2m', models.ManyToManyField(to='redis_ocm.M2M')),
            ],
        ),
        migrations.CreateModel(
            name='FKGP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('m2m', models.ManyToManyField(to='redis_ocm.FKP')),
            ],
        ),
    ]
