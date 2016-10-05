import ssim_api.ssim_general_functions as gf
import ssim_api.ssim_postprocessing_functions as sp
import ssim_api.ssim_query_functions as sq

from . import models


class StateClass(object):
    _query = lambda self: sq.db_query_stateclass

    def __init__(self):
        self._results = ()
        self.model = models.Scenario

    def __len__(self):
        return len(self._results)

    def __getitem__(self, idx):
        return self._results[idx]

    def _do_query(self, params):
        kw = params.copy()
        print(kw)
        aggregate = kw.pop('aggregate', None)
        percentile = kw.pop('percentile', None)
        scenarios = kw.pop('scenario', None)
        if not scenarios:
            return self.all()
        obj = self.model.objects.get(scenario=scenarios[0])
        db = obj.project.ssim.db
        self._results = self._query()(db.path, scenario_id=scenarios, **kw)
        if aggregate:
        	aggregate_by_columns = aggregate[0].split(",")
        	column = "Amount"
        	self._results = sp.aggregate_over(self._results, aggregate_by_columns, column)
        if percentile:
        	percentile_params = percentile[0].split(",")
        	percentile_params[1]=float(percentile_params[1])
        	percentile_params[2]=float(percentile_params[2])
        	print(percentile_params)
        	column = "Amount"
        	self._results = sp.calculate_percentile(self._results, percentile_params, column)
        return self

    def all(self):
        obj = self.model.objects.first()
        self._results = self._query()(obj.project.ssim.db.path,
                                      scenario_id=(obj.scenario,))
        return self

    def filter(self, **kwargs):
        return self._do_query(kwargs)

    def values(self):
        if self._results is not None:
            df = self._results
            df = df.where(df.notnull(), None)
            return df.to_dict('records')
        return []

    



class TransitionGroup(StateClass):
    _query = lambda self: sq.db_query_transitiongroup

class StockType(StateClass):
    _query = lambda self: sq.db_query_stock

class StockTypeNames(StateClass):
	def all(self):
	    obj = models.SyncroSim.objects.first()
	    self._results = gf.db_query_general(
	        obj.db.path, 'StockType',
	        table_name_project='SF_StockType')
	    return self


class TransitionGroupNames(StateClass):
    def all(self):
        obj = models.SyncroSim.objects.first()
        self._results = gf.db_query_general(
            obj.db.path, 'TransitionGroups',
            table_name_project='STSim_TransitionGroup')
        return self


class StateLabelNames(StateClass):
    def all(self):
        obj = self.model.objects.first()
        self._results = gf.db_query_general(
            obj.project.ssim.db.path, 'StateLabelX',
            table_name_project='STSim_StateLabelX')
        return self
