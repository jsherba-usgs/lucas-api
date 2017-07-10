from __future__ import unicode_literals

import os
import sqlite3
import uuid
import zipfile

from django.contrib.gis.db import models
from django.core.files.storage import default_storage
from django.template.defaultfilters import slugify
from spillway.models import AbstractRasterStore
from spillway.query import GeoQuerySet, RasterQuerySet

from .fields import VarCharField


class Tag(models.Model):
    name = VarCharField(unique=True)
    slug = models.SlugField(unique=True, max_length=64)

    def __unicode__(self):
        return self.name


class RasterSeries(models.Model):
    """A model representing a time series of 2D rasters."""
    name = VarCharField(blank=True, null=True)
    slug = models.SlugField(max_length=96)
    begin = models.DateTimeField()
    end = models.DateTimeField()
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ['slug']
        verbose_name_plural = 'raster series'

    def __unicode__(self):
        return self.slug


class RasterStore(AbstractRasterStore):
    """A model for file-based, geospatial raster storage."""
    unit_choices = (
        ('C', 'Celsius'),
        ('mm', 'millimeter'),
        ('m', 'meter'),
        ('K', 'Kelvin'),
        ('kg/m2/s', 'kilogram per square meter per second'),
    )
    name = VarCharField(blank=True, null=True)
    series = models.ForeignKey(RasterSeries, related_name='rasters',
                               blank=True, null=True)
    slug = models.SlugField(max_length=96, blank=True, null=True)
    units = models.CharField(choices=unit_choices, max_length=12,
                             blank=True, null=True)
    iteration = models.IntegerField(blank=True, null=True)
    scenarioval = models.IntegerField(blank=True, null=True)
    objects = RasterQuerySet.as_manager()

    def __unicode__(self):
        return self.slug


class SyncroSim(models.Model):
    """A model to manage SyncroSim SQLite databases."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    db = models.FileField()
    upload = models.FileField(blank=True, null=True)
    uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['db']
        verbose_name_plural = 'syncro sim'

    def __unicode__(self):
        return unicode(self.db)

    def fetch_source_rows(self, model):
        connection = sqlite3.connect(self.db.path)
        cursor = connection.cursor()
        fields = [field for field in model._meta.fields if field.db_column]
        columns = ', '.join(field.column for field in fields)
        params = {'columns': columns, 'table': model._meta.db_table}
        sql = 'SELECT {columns} FROM {table}'.format(**params)
        rows = cursor.execute(sql).fetchall()
        connection.close()
        attrs = [field.name for field in fields]
        return [dict(zip(attrs, row)) for row in rows]

    def load_projects(self):
        for row in self.fetch_source_rows(Project):
            project = Project(**row)
            project.ssim = self
            project.save()

    def load_scenarios(self):
        for row in self.fetch_source_rows(Scenario):
            row['project'] = Project.objects.get(project=row['project'])
            obj = Scenario(**row)
            obj.save()

    def save(self, *args, **kwargs):
        if self.upload:
            self.unpack()
        super(SyncroSim, self).save(*args, **kwargs)
        self.load_projects()
        self.load_scenarios()

    def unpack(self):
        zf = zipfile.ZipFile(self.upload)
        zf.extractall(default_storage.location)
        for name in zf.namelist():
            if name.endswith('.ssim'):
                self.db = default_storage.path(name)


class Project(models.Model):
    """A SyncroSim project."""
    project = models.IntegerField(db_column='ProjectID', blank=True, null=True)
    name = models.TextField(db_column='Name', blank=True, null=True)
    ssim = models.ForeignKey(SyncroSim)

    class Meta:
        db_table = 'SSim_Project'
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.project)


class Scenario(models.Model):
    """A SyncroSim scenario."""
    scenario = models.IntegerField(db_column='ScenarioID')
    project = models.ForeignKey(Project, db_column='ProjectID')
    name = models.TextField(db_column='Name', blank=True, null=True)
    author = models.TextField(db_column='Author', blank=True, null=True)
    description = models.TextField(db_column='Description',
                                   blank=True, null=True)
    is_read_only = models.BooleanField(db_column='IsReadOnly')
    runstatus = models.IntegerField(db_column='RunStatus',
                                    blank=True, null=True)
    runlog = models.TextField(db_column='RunLog', blank=True, null=True)
    last_modified = models.DateTimeField(db_column='DateLastModified',
                                         blank=True, null=True)
    rasters = models.ManyToManyField(RasterStore)

    class Meta:
        db_table = 'SSim_Scenario'
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.scenario)
