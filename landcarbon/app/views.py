from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.response import Response
from spillway import carto, renderers
from spillway.forms import VectorTileForm
from spillway.views import MapView, TileView
from spillway.viewsets import ReadOnlyGeoModelViewSet, ReadOnlyRasterModelViewSet

from . import forms, filters, models, pagination, query, serializers
from .renderers import CSVRenderer, PBFRenderer

ReadOnlyGeoModelViewSet.pagination_class = pagination.FeaturePagination


class ScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Scenario.objects.all()
    serializer_class = serializers.ScenarioSerializer
    lookup_field = 'scenario'


class StateListView(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = query.StateClass()

    def filter_queryset(self, queryset):
        data = self.request.query_params.copy()
        data.update(self.kwargs)
        form = forms.QueryForm(data)
        return queryset.filter(**form.params()).values()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset)


class TransitionListView(StateListView):
    queryset = query.TransitionGroup()


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
                        renderers.GeoJSONRenderer,
                        PBFRenderer)

    def get(self, request, layers=None, *args, **kwargs):
        layers = layers.split(',')
        views = filter(None, map(layerviews.get, layers))
        if not views:
            raise Http404('Layer does not exist')
        if not isinstance(request.accepted_renderer, renderers.MapnikRenderer):
            return Response(self.serialize_layers(views))
        form = VectorTileForm(dict(self.request.query_params.dict(),
                                   **self.kwargs))
        querysets = [v.queryset for v in views]
        m = carto.build_map(querysets, form)
        return Response(m.render(request.accepted_renderer.format))

    def serialize_layers(self, views):
        layers = {}
        for viewset in views:
            view = TileView(request=self.request, args=self.args,
                            kwargs=self.kwargs, queryset=viewset.queryset)
            view.format_kwarg = self.format_kwarg
            qs = view.filter_queryset(view.get_queryset())
            serializer = view.get_serializer(qs, many=True)
            layers[serializer.instance.model._meta.model_name] = serializer.data
        return layers
