from rest_framework import serializers
from spillway.serializers import RasterModelSerializer

from . import fields, models


class RasterStoreSerializer(RasterModelSerializer):
    tileurl = fields.RasterTileURLField(source='slug')
    url = serializers.HyperlinkedIdentityField(view_name='rasterstore-detail',
                                               lookup_field='slug')

    class Meta:
        model = models.RasterStore
        geom_field = 'geom'
        raster_field = 'image'
        exclude = ('series',)
        # extra_kwargs = {'url': {'lookup_field': 'slug'}}


class RasterSeriesSerializer(serializers.HyperlinkedModelSerializer):
    # rasters = serializers.HyperlinkedRelatedField(
        # many=True, read_only=True, lookup_field='slug',
        # view_name='rasterstore-detail')
    tags = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = models.RasterSeries
        fields = ('name', 'slug', 'url', 'begin', 'end', 'rasters', 'tags')
        extra_kwargs = {'rasters': {'lookup_field': 'slug'},
                        'url': {'lookup_field': 'slug'}}


class RasterCSVListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        rows = super(RasterCSVListSerializer, self).to_representation(data)
        return [dict(row, **d) for row in rows for d in row.pop('image')]


class RasterCSVSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RasterStore
        fields = ('slug', 'units')
        list_serializer_class = RasterCSVListSerializer

    def to_representation(self, obj):
        native = super(RasterCSVSerializer, self).to_representation(obj)
        native['image'] = [{'date': didx, 'value': val}
                           for didx, arr in enumerate(obj.image)
                           for val in arr.ravel()]
        return native
