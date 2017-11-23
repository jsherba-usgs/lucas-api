from django import forms
import math

from django.contrib.gis import gdal, forms
from greenwich.srs import transform_tile

from spillway import colors, query
from spillway.compat import ALL_TERMS
from spillway.forms import fields
from spillway.forms.forms import TileForm

def num_there(s):
        return any(i.isdigit() for i in s)

class QueryForm(forms.Form):
    scenario = forms.CharField(required=False)
    stratum = forms.CharField(required=False)
    secondary_stratum = forms.CharField(required=False)
    timestep = forms.CharField(required=False)
    iteration = forms.CharField(required=False, initial=1)
    group_by = forms.CharField(required=False)
    percentile = forms.CharField(required=False)


    def params(self):
        params = self.cleaned_data if self.is_valid() else {}
        
        for k, v in params.items():
            if not v:
                params.pop(k)
                continue
            if k=="percentile":
                params[k] = tuple([v.split(",")[0],int(v.split(",")[1])])
            else:
                if num_there(v)==True:
                    if "," not in v: 
                        params[k] = (int(v),)
                    else:
                        params[k] = tuple(map(int, v.split(",")))

                else:
                    if "," not in v: 
                        params[k] = (v,)
                    else:
                        params[k] = tuple(v.split(","))

        
        return params


class StateClassForm(QueryForm):
    state_label_x = forms.CharField(required=False)

class TransitionGroupForm(QueryForm):
    transition_group = forms.CharField(required=False)

class StockTypeForm(QueryForm):
    stock_type = forms.CharField(required=False)

class RasterTileForm(TileForm):
    band = forms.IntegerField(required=False, initial=1)
    size = forms.IntegerField(required=False, initial=256)
    limits = fields.CommaSepFloatField(required=False)
    style = forms.CharField(required=False)
    def clean(self):
        data = super(TileForm, self).clean()
        print(data)
        x, y, z = map(data.get, ('x', 'y', 'z'))
        # Create bbox from NW and SE tile corners.

        try:
            
            #extent = (transform_tile(x, y, z) +
            #          transform_tile(x + 1, y + 1, z))
            
            #extent =-159.85461369, 22.3883299982, -154.459224592, 18.7379531081)
            extent = (-124.473333, 42.005860, -114.144959, 32.532193)
    
        except TypeError:
            pass
        else:
           
            geom = gdal.OGRGeometry.from_bbox(extent)
            geom.srid = self.fields['bbox'].srid
            data['bbox'] = geom
        return data


    def clean_band(self):
        return self.cleaned_data['band'] or self.fields['band'].initial

    def clean_style(self):
        # Mapnik requires string, not unicode, for style names.
        return str(self.cleaned_data['style'])