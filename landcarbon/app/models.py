from __future__ import unicode_literals

import os
import uuid

from django.contrib.gis.db import models
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
    objects = RasterQuerySet.as_manager()

    def __unicode__(self):
        return self.slug
