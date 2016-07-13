import django_filters
from rest_framework import filters

from . import models


class URLFilterBackend(filters.DjangoFilterBackend):
    """A backend to filter on URL path based kwargs."""

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)
        if filter_class:
            return filter_class(view.kwargs, queryset=queryset).qs
        return queryset


class RasterStoreFilterSet(django_filters.FilterSet):
    begin = django_filters.DateFilter(name='event', lookup_type='gte')
    end = django_filters.DateFilter(name='event', lookup_type='lte')

    class Meta:
        model = models.RasterStore
        fields = ('series__slug', 'begin', 'end')


class RasterSeriesFilterSet(django_filters.FilterSet):
    tags = django_filters.MultipleChoiceFilter(
        name='tags__name', lookup_type='iexact', conjoined=True)

    class Meta:
        model = models.RasterSeries
        fields = ('name', 'slug', 'tags')
