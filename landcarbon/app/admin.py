from django.contrib import admin

from . import models

_models = (
    models.RasterSeries,
    models.RasterStore,
    models.Tag,
)

for _model in _models:
    admin.site.register(_model)


@admin.register(models.Project)
class SyncroSimAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'ssim')


@admin.register(models.Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    date_hierarchy = 'last_modified'
    list_display = ('scenario', 'name', 'project', 'author')


@admin.register(models.SyncroSim)
class SyncroSimAdmin(admin.ModelAdmin):
    list_display = ('db', 'id')
