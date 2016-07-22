from django import forms

MOISTURE_ZONES = ('Dry', 'Wet', 'Mesic')
ISLANDS = ("Hawai'i", 'Maui', "O'ahu")

def repeat_items(lst, n=2):
    return [(item,) * n for item in lst]


class QueryForm(forms.Form):
    scenario = forms.IntegerField(required=False)
    stratum_choices = repeat_items(MOISTURE_ZONES)
    stratum = forms.MultipleChoiceField(
        choices=stratum_choices, required=False)
    secondary_stratum = forms.MultipleChoiceField(
        choices=repeat_items(ISLANDS), required=False)
    timestep = forms.IntegerField(required=False)

    def params(self):
        params = self.cleaned_data if self.is_valid() else {}
        for k, v in params.items():
            if not v:
                params.pop(k)
                continue
            if isinstance(v, list):
                params[k] = tuple(v)
            elif not isinstance(v, tuple):
                params[k] = (v,)
        return params
