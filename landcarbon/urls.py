from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.http import HttpResponse

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^robots.txt$', lambda _: HttpResponse('User-agent: *\nDisallow: /',
                                                content_type='text/plain')),
    url(r'', include('landcarbon.app.urls')),
]

# Support serving static/media roots and tilesets during development.
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    from django.conf.urls.static import static
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += (
        # url('^tiles/(?P<path>.*)', RedirectView.as_view(
            # url='http://localhost:8080/%(path)s', query_string=True)),
    # )
