from django.conf.urls import url, include
from rest_framework import routers

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

    url(r'^tiles/(?P<slug>[\w-]+)/%s' % _tile,
        views.RasterMapView.as_view(), name='raster-tiles'),
    url(r'^vtiles/(?P<layers>[\w,]+)/%s' % _tile,
        views.TileLayersView.as_view(), name='vectorlayer-tiles'),
]
