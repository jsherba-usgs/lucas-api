import ssim_api.ssim_query_functions as sq
import ssim_api.ssim_postprocessing_functions as sp

from . import forms, models


class SimQuery(object):
    def __init__(self, scenario, request):
        self.scenario = scenario.scenario
        self.db = scenario.project.ssim.db
        form = forms.QueryForm(request.query_params)
        self.params = form.params()

    def build_query(self, fn):
        return fn(self.db.path, scenario_id=(self.scenario,), **self.params)

    def stateclasses(self):
        return self.build_query(sq.db_query_stateclass)

    def transitiongroups(self):
        return self.build_query(sq.db_query_transitiongroup)
