from django.http import Http404
from rest_framework.renderers import JSONRenderer
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.views import APIView
from rest_framework.settings import api_settings
#from rest_framework_csv import renderers as r
from rest_framework import generics, viewsets
from rest_framework.response import Response
from spillway import carto, renderers
from spillway.forms import VectorTileForm
from spillway.views import MapView, TileView
from spillway.viewsets import ReadOnlyGeoModelViewSet, ReadOnlyRasterModelViewSet, GenericGeoViewSet

from . import forms, filters, models, pagination, query, serializers
from .renderers import CSVRenderer, PaginatedCSVRenderer, PBFRenderer

ReadOnlyGeoModelViewSet.pagination_class = pagination.FeaturePagination


class ScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Scenario.objects.all()
    serializer_class = serializers.ScenarioSerializer
    lookup_field = 'scenario'


class QueryFormViewSet(viewsets.ReadOnlyModelViewSet):
    queryform = None

    def filter_queryset(self, queryset):
        form = self.queryform(self.request.query_params.copy())
        return queryset.filter(**form.params()).values()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset)


class StateListView(QueryFormViewSet):
    queryset = query.StateClass()
    renderer_classes = (BrowsableAPIRenderer,JSONRenderer, PaginatedCSVRenderer)
    queryform = forms.StateClassForm

    


class StateLabelView(QueryFormViewSet):
    queryset = query.StateLabelNames()
    queryform = forms.StateClassForm


class TransitionListView(QueryFormViewSet):
    queryset = query.TransitionGroup()
    renderer_classes = (BrowsableAPIRenderer,JSONRenderer, PaginatedCSVRenderer)
    queryform = forms.TransitionGroupForm


class TransitionGroupView(QueryFormViewSet):
    queryset = query.TransitionGroupNames()
    queryform = forms.TransitionGroupForm

class StockTypeView(QueryFormViewSet):
    queryset = query.StockType()
    renderer_classes = (BrowsableAPIRenderer,JSONRenderer, PaginatedCSVRenderer)
    queryform = forms.StockTypeForm

class StockTypeListView(QueryFormViewSet):
    queryset = query.StockTypeNames()
    queryform = forms.StockTypeForm


class RasterSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.RasterSeries.objects.prefetch_related(
        'rasters', 'tags')
    serializer_class = serializers.RasterSeriesSerializer
    filter_class = filters.RasterSeriesFilterSet
    lookup_field = 'slug'


class RasterStoreViewSet(ReadOnlyRasterModelViewSet):
    queryset = models.RasterStore.objects.all()
    serializer_class = serializers.RasterStoreSerializer
    renderer_classes = (ReadOnlyRasterModelViewSet.renderer_classes +
                        (CSVRenderer,))
   
    filter_backends = (filters.URLFilterBackend,)
    #filter_backends = (DjangoFilterBackend,)
    #filter_class = ("iteration",)#
    filter_class = filters.RasterStoreFilterSet
    lookup_field = 'slug'

    def get_serializer(self, *args, **kwargs):

        renderer = self.request.accepted_renderer
        if isinstance(renderer, CSVRenderer):
            self.serializer_class = serializers.RasterCSVSerializer
        return super(RasterStoreViewSet, self).get_serializer(*args, **kwargs)


class RasterMapView(MapView):
    queryset = models.RasterStore.objects.all()
    lookup_field = 'slug'



class TileLayersView(TileView):
    renderer_classes = (renderers.MapnikRenderer,
                        renderers.GeoJSONRenderer)
    
    queryset = models.Location.objects.all()    
    def get_queryset(self):
        return models.Location.objects.filter(layers=self.kwargs['layers'])
        
        
        