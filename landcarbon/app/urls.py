from django.conf.urls import url, include
from django.views.decorators.cache import cache_page
from rest_framework import routers
from spillway import generics
from spillway import views
from .models import Location
from . import views

router = routers.DefaultRouter()
router.register(r'series', views.RasterSeriesViewSet)
router.register(r'rstores', views.RasterStoreViewSet)
router.register(r'stateclasses', views.StateListView, 'stateclasses')
router.register(r'statelabels', views.StateLabelView, 'statelabels')
router.register(r'transitions', views.TransitionListView, 'transitions')
router.register(r'transitiongroups', views.TransitionGroupView, 'transitiongroups')
router.register(r'stocktypes', views.StockTypeView, 'stocktypes')
router.register(r'stocktypesnames', views.StockTypeListView, 'stocktypesnames')
_format_suffix = r'(?:\.(?P<format>[\w.]+))?'
_tile = r'(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)%s/?$' % _format_suffix

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url((r'^api/series/(?P<series__slug>[\w-]+)/'
         r'(rasters|(?P<begin>[\d-]+))/((?P<end>[\d-]+)/)?$'),
        views.RasterStoreViewSet.as_view({'get': 'list'}),
        name='rasterstore-series-list'),

    #url(r'^tiles/(?P<slug>[\w-]+)/%s' % _tile,
    #    views.RasterMapView.as_view(), name='raster-tiles'),
    url(r'^tiles/(?P<slug>[\w-]+)/%s' % _tile,
         view = cache_page(None)(views.RasterMapView.as_view()),
         name='raster-tiles'),
    url(r'^vtiles/(?P<layers>[\w,]+)/%s' % _tile,
        views.TileLayersView.as_view(), name='vectorlayer-tiles'),
    #url(r'^vtiles/?P<layers>[\w,]+)/%s' % _tile,
       ## views.TileView.as_view(),
        #name='location-tiles'),
    url(r'^locations/(?P<slug>[\w-]+)/$',
        generics.GeoDetailView.as_view(queryset=Location.objects.all(), lookup_field='slug'),
        name='location'),
    url(r'^locations/$',
        generics.GeoListView.as_view(queryset=Location.objects.all()),
        name='location-list'),


]
