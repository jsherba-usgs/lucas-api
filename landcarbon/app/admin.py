from django.contrib import admin

from . import models

admin.site.register(models.RasterSeries)
admin.site.register(models.RasterStore)
admin.site.register(models.Tag)
