from django.http import Http404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from spillway import carto, forms, renderers
from spillway.views import MapView, TileView
from spillway.viewsets import ReadOnlyGeoModelViewSet, ReadOnlyRasterModelViewSet

from . import filters, models, pagination, serializers
from .renderers import CSVRenderer, PBFRenderer

ReadOnlyGeoModelViewSet.pagination_class = pagination.FeaturePagination


class ScenarioViewSet(ReadOnlyModelViewSet):
    queryset = models.Scenario.objects.all()
    serializer_class = serializers.ScenarioSerializer
    lookup_field = 'scenario'


class ScenarioDetailView(RetrieveAPIView):
    queryset = models.Scenario.objects.all()
    serializer_class = serializers.ScenarioSerializer
    lookup_field = 'scenario'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.query_params:
            q = query.SimQuery(instance, request)
            data = q.stateclasses().to_dict('records')
            return Response(data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class StateListView(ScenarioDetailView):
    def get_object(self):
        instance = super(StateListView, self).get_object()
        return query.SimQuery(instance, self.request).stateclasses()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.to_dict('records'))


class TransitionListView(StateListView):
    def get_object(self):
        instance = super(TransitionListView, self).get_object()
        return query.SimQuery(instance, self.request).transitiongroups()


class RasterSeriesViewSet(ReadOnlyModelViewSet):
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
        form = forms.VectorTileForm(dict(self.request.query_params.dict(),
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
