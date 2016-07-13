import urllib

from django.db.models.fields import CharField
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse


# https://djangosnippets.org/snippets/2328/
class VarCharField(CharField):
    """A basically unlimited-length CharField."""
    description = _('Unlimited-length string')

    def __init__(self, *args, **kwargs):
        # kwargs['max_length'] = None # doesn't work
        # kwargs['max_length'] = int(1e9)
        # Satisfy management validation.
        kwargs['max_length'] = 255
        super(CharField, self).__init__(*args, **kwargs)
        # Don't add max-length validator like CharField does.

    def get_internal_type(self):
        # This has no function, since this value is used as a lookup in
        # db_type(). Put something that isn't known by django so it raises an
        # error if it is ever used.
        return 'VarCharField'

    def db_type(self, connection):
        # *** This is probably only compatible with Postgres.
        # 'varchar' with no max length is equivalent to 'text' in Postgres, but
        # put 'varchar' so we can tell LongCharFields from TextFields when
        # we're looking at the db.
        return 'varchar'

    def formfield(self, **kwargs):
        # Don't pass max_length to form field like CharField does.
        return super(CharField, self).formfield(**kwargs)


class RasterTileURLField(serializers.URLField):
    """Returns a URL template for retrieving raster map tiles."""

    def to_representation(self, value):
        urltemplate = '/{z}/{x}/{y}'
        urlargs = [value, 0, 0, 0, 'png']
        request = self.context.get('request')
        urlabspath = reverse('raster-tiles', args=urlargs, request=request)
        return urlabspath.replace('/0/0/0', urltemplate)
