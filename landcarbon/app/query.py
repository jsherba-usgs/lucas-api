import ssim_api.ssim_query_functions as sq
import ssim_api.ssim_postprocessing_functions as sp

from . import forms, models


class StateClass(object):
    _query = lambda self: sq.db_query_stateclass

    def __init__(self):
        self._results = ()

    def __len__(self):
        return len(self._results)

    def __getitem__(self, idx):
        return self._results[idx]

    def _do_query(self, params):
        kw = params.copy()
        scenarios = kw.pop('scenario')
        obj = models.Scenario.objects.get(scenario=scenarios[0])
        db = obj.project.ssim.db
        self._results = self._query()(db.path, scenario_id=scenarios, **kw)
        return self

    def filter(self, **kwargs):
        return self._do_query(kwargs)

    def values(self):
        return self._results.to_dict('records')


class TransitionGroup(StateClass):
    _query = lambda self: sq.db_query_transitiongroup
