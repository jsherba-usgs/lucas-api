from django import forms


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
        print(params)
        '''for k, v in params.items():
            if not v:
                params.pop(k)
                continue
            if isinstance(v, list):
                params[k] = tuple(v)
            elif not isinstance(v, tuple):
                params[k] = (v,)'''
        for k, v in params.items():
            if not v:
                params.pop(k)
                continue
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

        print(params)
        return params


class StateClassForm(QueryForm):
    state_label_x = forms.CharField(required=False)

class TransitionGroupForm(QueryForm):
    transition_group = forms.CharField(required=False)

class StockTypeForm(QueryForm):
    stock_type = forms.CharField(required=False)