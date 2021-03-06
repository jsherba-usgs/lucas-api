# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-14 18:37
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import landcarbon.app.fields
import spillway.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RasterSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', landcarbon.app.fields.VarCharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(max_length=96)),
                ('begin', models.DateTimeField()),
                ('end', models.DateTimeField()),
            ],
            options={
                'ordering': ['slug'],
                'verbose_name_plural': 'raster series',
            },
        ),
        migrations.CreateModel(
            name='RasterStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to=spillway.models.UploadDir(b'data'), verbose_name='raster file')),
                ('width', models.IntegerField(verbose_name='width in pixels')),
                ('height', models.IntegerField(verbose_name='height in pixels')),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=4326, verbose_name='raster bounding polygon')),
                ('event', models.DateField()),
                ('srs', models.TextField(verbose_name='spatial reference system')),
                ('minval', models.FloatField(verbose_name='minimum value')),
                ('maxval', models.FloatField(verbose_name='maximum value')),
                ('nodata', models.FloatField(blank=True, null=True, verbose_name='nodata value')),
                ('xpixsize', models.FloatField(verbose_name='West to East pixel resolution')),
                ('ypixsize', models.FloatField(verbose_name='North to South pixel resolution')),
                ('name', landcarbon.app.fields.VarCharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(blank=True, max_length=96, null=True)),
                ('units', models.CharField(blank=True, choices=[('C', 'Celsius'), ('mm', 'millimeter'), ('m', 'meter'), ('K', 'Kelvin'), ('kg/m2/s', 'kilogram per square meter per second')], max_length=12, null=True)),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rasters', to='app.RasterSeries')),
            ],
            options={
                'ordering': ['image'],
                'abstract': False,
                'get_latest_by': 'event',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', landcarbon.app.fields.VarCharField(max_length=255, unique=True)),
                ('slug', models.SlugField(max_length=64, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='rasterseries',
            name='tags',
            field=models.ManyToManyField(blank=True, to='app.Tag'),
        ),
        migrations.AlterUniqueTogether(
            name='rasterstore',
            unique_together=set([('image', 'event')]),
        ),
    ]
