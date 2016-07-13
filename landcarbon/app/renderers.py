import csv
import io

import mapbox_vector_tile
from rest_framework.renderers import BaseRenderer


class CSVRenderer(BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'
    charset = 'utf-8'
    render_style = 'text'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict):
            fields = data.keys()
            data = [data]
        else:
            fields = data[0].keys() if len(data) else []
        fp = io.BytesIO()
        writer = csv.DictWriter(fp, fields)
        writer.writeheader()
        writer.writerows(data)
        fp.seek(0)
        return fp


# According to the spec, file extension SHOULD be mvt and mime SHOULD be
# application/vnd.mapbox-vector-tile though mapbox uses .vector.pbf for their
# vector tiles. See spec:
# https://github.com/mapbox/vector-tile-spec/tree/master/2.1
# key word is "SHOULD", not "MUST". Decide which mime/ext to use here.
class PBFRenderer(BaseRenderer):
    media_type = 'application/x-protobuf'
    format = 'pbf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        layers = [{'name': k, 'features': v['features']}
                  for k, v in data.items()]
                  # for k, v in data.iteritems()]
        # TODO: Use wkb instead of wkt. Better yet, avoid extra roundtrip with
        # shapely geom serialization.
        return mapbox_vector_tile.encode(layers)
