from django import forms


class QueryForm(forms.Form):
    scenario = forms.IntegerField(required=False)
    stratum = forms.CharField(required=False)
    secondary_stratum = forms.CharField(required=False)
    timestep = forms.IntegerField(required=False)
    iteration = forms.IntegerField(required=False, initial=1)

    def params(self):
        params = self.cleaned_data if self.is_valid() else {}
        print(params)
        for k, v in params.items():
            if not v:
                params.pop(k)
                continue
            if isinstance(v, list):
                params[k] = tuple(v)
            elif not isinstance(v, tuple):
                params[k] = (v,)
        return params


class StateClassForm(QueryForm):
    state_label_x = forms.CharField(required=False)

class TransitionGroupForm(QueryForm):
    transition_group = forms.CharField(required=False)

class StockTypeForm(QueryForm):
    stock_type = forms.CharField(required=False)