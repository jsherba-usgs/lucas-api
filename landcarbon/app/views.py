from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from spillway import carto, forms, renderers
from spillway.views import MapView, TileView
from spillway.viewsets import ReadOnlyGeoModelViewSet, ReadOnlyRasterModelViewSet

from . import filters, models, pagination, serializers
from .renderers import CSVRenderer, PBFRenderer

ReadOnlyGeoModelViewSet.pagination_class = pagination.FeaturePagination


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
